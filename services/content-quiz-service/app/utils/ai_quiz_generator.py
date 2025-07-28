"""
AI Quiz Question Generator
AI-powered quiz question generation with multiple question types
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from ..database import get_db
from ..models.content_models import Quiz, Question, Course, Subject
from ..utils.cache import cache_result, invalidate_cache_pattern

import logging
import json
import openai
import random
from datetime import datetime

logger = logging.getLogger(__name__)

# OpenAI client setup (configure with your API key)
# openai.api_key = os.getenv("OPENAI_API_KEY")


class QuestionGenerator:
    """AI-powered question generator for quizzes"""
    
    def __init__(self):
        self.question_templates = {
            "multiple_choice": {
                "prompt_template": """Generate a multiple choice question about {topic} at {difficulty} difficulty level.
                
                Requirements:
                - Question should be clear and specific
                - Provide 4 answer options (A, B, C, D)
                - Only one correct answer
                - Distractors should be plausible but clearly incorrect
                - Include a brief explanation of the correct answer
                
                Format as JSON:
                {{
                    "question_text": "Question here?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": "A",
                    "explanation": "Explanation here",
                    "difficulty": "{difficulty}",
                    "tags": ["tag1", "tag2"]
                }}""",
                "points": {"easy": 1, "intermediate": 2, "hard": 3}
            },
            
            "true_false": {
                "prompt_template": """Generate a true/false question about {topic} at {difficulty} difficulty level.
                
                Requirements:
                - Statement should be clear and unambiguous
                - Avoid absolute terms unless actually absolute
                - Include explanation for the correct answer
                
                Format as JSON:
                {{
                    "question_text": "Statement here.",
                    "correct_answer": true,
                    "explanation": "Explanation here",
                    "difficulty": "{difficulty}",
                    "tags": ["tag1", "tag2"]
                }}""",
                "points": {"easy": 1, "intermediate": 1, "hard": 2}
            },
            
            "short_answer": {
                "prompt_template": """Generate a short answer question about {topic} at {difficulty} difficulty level.
                
                Requirements:
                - Question should elicit a 1-3 word answer
                - Answer should be specific and factual
                - Avoid questions with multiple correct answers
                
                Format as JSON:
                {{
                    "question_text": "Question here?",
                    "correct_answer": "Expected answer",
                    "explanation": "Explanation here",
                    "difficulty": "{difficulty}",
                    "tags": ["tag1", "tag2"]
                }}""",
                "points": {"easy": 2, "intermediate": 3, "hard": 4}
            },
            
            "fill_blank": {
                "prompt_template": """Generate a fill-in-the-blank question about {topic} at {difficulty} difficulty level.
                
                Requirements:
                - Create a sentence with 1-2 blanks marked with ___
                - Blanks should test key concepts
                - Answers should be specific terms or phrases
                
                Format as JSON:
                {{
                    "question_text": "Complete sentence with ___ blanks.",
                    "correct_answer": "word to fill blank",
                    "explanation": "Explanation here",
                    "difficulty": "{difficulty}",
                    "tags": ["tag1", "tag2"]
                }}""",
                "points": {"easy": 2, "intermediate": 3, "hard": 4}
            }
        }
    
    def generate_topic_context(self, topic: str, course_name: str, subject_name: str) -> str:
        """Generate context for the topic based on course and subject"""
        return f"""
        Topic: {topic}
        Course: {course_name}
        Subject: {subject_name}
        
        Focus on practical, educational content appropriate for this academic context.
        Questions should test understanding, application, and analysis of the topic.
        """
    
    def generate_question_prompt(
        self,
        question_type: str,
        topic: str,
        difficulty: str,
        course_name: str,
        subject_name: str,
        existing_questions: List[str] = None
    ) -> str:
        """Generate a prompt for AI question generation"""
        
        if question_type not in self.question_templates:
            raise ValueError(f"Unsupported question type: {question_type}")
        
        template = self.question_templates[question_type]["prompt_template"]
        context = self.generate_topic_context(topic, course_name, subject_name)
        
        prompt = context + "\n\n" + template.format(
            topic=topic,
            difficulty=difficulty
        )
        
        # Add uniqueness requirement if existing questions provided
        if existing_questions:
            prompt += f"\n\nExisting questions to avoid duplicating:\n"
            for i, eq in enumerate(existing_questions[-5:], 1):  # Show last 5 questions
                prompt += f"{i}. {eq}\n"
            prompt += "\nEnsure the new question is unique and covers different aspects."
        
        return prompt
    
    def parse_ai_response(self, response_text: str, question_type: str) -> Dict[str, Any]:
        """Parse AI response into structured question data"""
        try:
            # Try to parse as JSON
            if response_text.strip().startswith('{'):
                question_data = json.loads(response_text)
            else:
                # Extract JSON from response text
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    question_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            
            # Validate required fields
            required_fields = ["question_text", "correct_answer", "explanation"]
            for field in required_fields:
                if field not in question_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Set default values
            question_data.setdefault("difficulty", "intermediate")
            question_data.setdefault("tags", [])
            
            # Question type specific validation
            if question_type == "multiple_choice":
                if "options" not in question_data or len(question_data["options"]) < 4:
                    raise ValueError("Multiple choice questions need 4 options")
            
            return question_data
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Failed to parse AI response: {e}")
    
    def generate_fallback_question(self, topic: str, question_type: str, difficulty: str) -> Dict[str, Any]:
        """Generate a fallback question when AI generation fails"""
        
        fallback_questions = {
            "multiple_choice": {
                "question_text": f"Which of the following is most relevant to {topic}?",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A",
                "explanation": f"This is a fallback question about {topic}. Please review and update manually."
            },
            "true_false": {
                "question_text": f"{topic} is an important concept in this subject.",
                "correct_answer": True,
                "explanation": f"This is a fallback statement about {topic}. Please review and update manually."
            },
            "short_answer": {
                "question_text": f"What is the key aspect of {topic}?",
                "correct_answer": "Key aspect",
                "explanation": f"This is a fallback question about {topic}. Please review and update manually."
            }
        }
        
        base_question = fallback_questions.get(question_type, fallback_questions["multiple_choice"])
        base_question.update({
            "difficulty": difficulty,
            "tags": [topic.lower().replace(" ", "_"), "ai_generated", "fallback"],
        })
        
        return base_question
    
    async def generate_single_question(
        self,
        topic: str,
        question_type: str,
        difficulty: str,
        course_name: str,
        subject_name: str,
        existing_questions: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a single question using AI"""
        
        try:
            # Generate prompt
            prompt = self.generate_question_prompt(
                question_type, topic, difficulty, course_name, subject_name, existing_questions
            )
            
            # Mock AI response (replace with actual AI call)
            # response = await openai.ChatCompletion.acreate(
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "user", "content": prompt}],
            #     max_tokens=500,
            #     temperature=0.7
            # )
            # response_text = response.choices[0].message.content
            
            # For now, use fallback (replace with actual AI implementation)
            logger.warning("Using fallback question generation (AI not configured)")
            question_data = self.generate_fallback_question(topic, question_type, difficulty)
            
            # Add points based on difficulty and type
            points = self.question_templates[question_type]["points"].get(difficulty, 2)
            question_data["points"] = points
            
            return question_data
            
        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            # Use fallback
            question_data = self.generate_fallback_question(topic, question_type, difficulty)
            points = self.question_templates[question_type]["points"].get(difficulty, 2)
            question_data["points"] = points
            return question_data


async def generate_quiz_questions(
    quiz_id: int,
    topic: str,
    num_questions: int,
    difficulty: str,
    user_id: int
):
    """Generate multiple questions for a quiz using AI"""
    
    db = next(get_db())
    generator = QuestionGenerator()
    
    try:
        # Get quiz details
        quiz = db.query(Quiz).options(
            joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Quiz.id == quiz_id).first()
        
        if not quiz:
            logger.error(f"Quiz {quiz_id} not found")
            return
        
        course_name = quiz.course.name
        subject_name = quiz.course.subject.name
        
        # Get existing questions to avoid duplicates
        existing_questions = db.query(Question.question_text).filter(
            Question.quiz_id == quiz_id,
            Question.is_active == True
        ).all()
        existing_question_texts = [q[0] for q in existing_questions]
        
        # Question types to generate (you can make this configurable)
        question_types = ["multiple_choice", "true_false", "short_answer"]
        if num_questions >= 5:
            question_types.append("fill_blank")
        
        # Generate questions
        generated_questions = []
        max_order = db.query(func.max(Question.order_index)).filter(
            Question.quiz_id == quiz_id
        ).scalar() or 0
        
        for i in range(num_questions):
            try:
                # Vary question types
                question_type = question_types[i % len(question_types)]
                
                # Generate question
                question_data = await generator.generate_single_question(
                    topic=topic,
                    question_type=question_type,
                    difficulty=difficulty,
                    course_name=course_name,
                    subject_name=subject_name,
                    existing_questions=existing_question_texts
                )
                
                # Create question in database
                new_question = Question(
                    quiz_id=quiz_id,
                    question_text=question_data["question_text"],
                    question_type=question_type,
                    options=question_data.get("options"),
                    correct_answer=question_data["correct_answer"],
                    points=question_data["points"],
                    order_index=max_order + i + 1,
                    explanation=question_data["explanation"],
                    difficulty=question_data["difficulty"],
                    tags=question_data.get("tags", []),
                    created_by=user_id,
                    is_active=True
                )
                
                db.add(new_question)
                generated_questions.append(new_question)
                
                # Add to existing questions list to avoid duplicates
                existing_question_texts.append(question_data["question_text"])
                
            except Exception as e:
                logger.error(f"Error generating question {i+1}: {e}")
                continue
        
        # Commit all questions
        db.commit()
        
        # Update quiz question count
        quiz.question_count = db.query(func.count(Question.id)).filter(
            Question.quiz_id == quiz_id,
            Question.is_active == True
        ).scalar()
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quiz:{quiz_id}:*")
        invalidate_cache_pattern(f"questions:*")
        
        logger.info(f"Generated {len(generated_questions)} AI questions for quiz {quiz_id}")
        
        return {
            "success": True,
            "generated_count": len(generated_questions),
            "quiz_id": quiz_id,
            "topic": topic,
            "difficulty": difficulty
        }
        
    except Exception as e:
        logger.error(f"Error in AI question generation: {e}")
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "generated_count": 0
        }
    finally:
        db.close()


def get_question_difficulty_distribution(num_questions: int) -> Dict[str, int]:
    """Get optimal difficulty distribution for a set of questions"""
    
    if num_questions <= 3:
        return {"easy": num_questions, "intermediate": 0, "hard": 0}
    elif num_questions <= 5:
        return {"easy": 2, "intermediate": num_questions - 2, "hard": 0}
    elif num_questions <= 10:
        easy_count = max(1, num_questions // 4)
        hard_count = max(1, num_questions // 5)
        intermediate_count = num_questions - easy_count - hard_count
        return {"easy": easy_count, "intermediate": intermediate_count, "hard": hard_count}
    else:
        easy_count = max(2, num_questions // 4)
        hard_count = max(2, num_questions // 4)
        intermediate_count = num_questions - easy_count - hard_count
        return {"easy": easy_count, "intermediate": intermediate_count, "hard": hard_count}


def get_question_type_distribution(num_questions: int) -> Dict[str, int]:
    """Get optimal question type distribution"""
    
    # Base distribution
    distribution = {
        "multiple_choice": max(1, num_questions // 2),
        "true_false": max(1, num_questions // 5),
        "short_answer": max(1, num_questions // 4)
    }
    
    # Add remaining questions to multiple choice
    assigned = sum(distribution.values())
    if assigned < num_questions:
        distribution["multiple_choice"] += num_questions - assigned
    
    # Add fill_blank for larger quizzes
    if num_questions >= 8:
        distribution["fill_blank"] = max(1, num_questions // 8)
        distribution["multiple_choice"] -= distribution["fill_blank"]
    
    return {k: v for k, v in distribution.items() if v > 0}
