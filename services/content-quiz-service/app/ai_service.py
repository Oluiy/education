"""
EduNerve Content & Quiz Service - AI Integration
OpenAI GPT integration for quiz generation and grading
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import logging

from app.schemas import QuizQuestion, MCQOption, DifficultyLevel, QuizType

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class AIQuizGenerator:
    """AI-powered quiz generation using OpenAI GPT"""
    
    def __init__(self):
        self.client = client
        self.model = DEFAULT_MODEL
    
    def generate_quiz(
        self,
        content_text: str,
        subject: str,
        class_level: str,
        topic: Optional[str] = None,
        difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM,
        quiz_type: QuizType = QuizType.MCQ,
        num_questions: int = 10
    ) -> tuple[List[QuizQuestion], str]:
        """
        Generate quiz questions using OpenAI GPT
        
        Returns:
            tuple: (questions_list, generation_prompt)
        """
        try:
            # Create the prompt
            prompt = self._create_quiz_prompt(
                content_text, subject, class_level, topic,
                difficulty_level, quiz_type, num_questions
            )
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Nigerian secondary school teacher specialized in creating WAEC-standard examination questions. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            questions_data = json.loads(response_text)
            
            # Convert to QuizQuestion objects
            questions = self._parse_questions(questions_data, quiz_type)
            
            logger.info(f"Generated {len(questions)} questions for {subject} - {class_level}")
            return questions, prompt
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
    def _create_quiz_prompt(
        self,
        content_text: str,
        subject: str,
        class_level: str,
        topic: Optional[str],
        difficulty_level: DifficultyLevel,
        quiz_type: QuizType,
        num_questions: int
    ) -> str:
        """Create the AI prompt for quiz generation"""
        
        # Base prompt structure
        prompt = f"""
Generate {num_questions} {quiz_type.value} questions for {subject} at {class_level} level.
Difficulty: {difficulty_level.value}
{f"Topic: {topic}" if topic else ""}

Content to base questions on:
{content_text[:3000]}  # Truncate to avoid token limits

Requirements:
1. Questions must be appropriate for Nigerian secondary school students
2. Follow WAEC examination standards
3. Use clear, simple English
4. Include relevant Nigerian context where applicable
5. Each question should test understanding, not just memorization

"""
        
        if quiz_type == QuizType.MCQ:
            prompt += """
Format your response as JSON with this structure:
{
  "questions": [
    {
      "question_id": "q1",
      "question_text": "What is...?",
      "options": [
        {"text": "Option A", "is_correct": false},
        {"text": "Option B", "is_correct": true},
        {"text": "Option C", "is_correct": false},
        {"text": "Option D", "is_correct": false}
      ],
      "marks": 1.0,
      "explanation": "Brief explanation of the correct answer"
    }
  ]
}

Guidelines for MCQ:
- Provide exactly 4 options (A, B, C, D)
- Only one correct answer per question
- Make distractors plausible but clearly incorrect
- Avoid "all of the above" or "none of the above"
- Each question worth 1 mark
"""
        
        elif quiz_type == QuizType.THEORY:
            prompt += """
Format your response as JSON with this structure:
{
  "questions": [
    {
      "question_id": "q1",
      "question_text": "Explain the concept of...?",
      "marks": 5.0,
      "suggested_answer": "A comprehensive answer covering...",
      "grading_criteria": [
        "Student mentions key concept A",
        "Student provides relevant example",
        "Student explains the relationship between X and Y"
      ]
    }
  ]
}

Guidelines for Theory:
- Questions should require explanation, analysis, or application
- Marks range from 2-10 based on complexity
- Provide detailed suggested answers
- Include specific grading criteria
- Use action verbs: explain, analyze, compare, evaluate, discuss
"""
        
        else:  # MIXED
            prompt += """
Format your response as JSON with this structure:
{
  "questions": [
    {
      "question_id": "q1",
      "question_type": "mcq",
      "question_text": "What is...?",
      "options": [
        {"text": "Option A", "is_correct": false},
        {"text": "Option B", "is_correct": true},
        {"text": "Option C", "is_correct": false},
        {"text": "Option D", "is_correct": false}
      ],
      "marks": 1.0,
      "explanation": "Brief explanation"
    },
    {
      "question_id": "q2",
      "question_type": "theory",
      "question_text": "Explain...",
      "marks": 5.0,
      "suggested_answer": "Detailed answer...",
      "grading_criteria": ["Point 1", "Point 2"]
    }
  ]
}

Guidelines for Mixed:
- Include both MCQ and theory questions
- Balance the number of each type
- Ensure variety in question complexity
"""
        
        return prompt
    
    def _parse_questions(self, questions_data: Dict, quiz_type: QuizType) -> List[QuizQuestion]:
        """Parse AI response into QuizQuestion objects"""
        questions = []
        
        for i, q_data in enumerate(questions_data.get("questions", [])):
            try:
                question = QuizQuestion(
                    question_id=q_data.get("question_id", f"q{i+1}"),
                    question_type=q_data.get("question_type", quiz_type.value),
                    question_text=q_data["question_text"],
                    marks=float(q_data.get("marks", 1.0)),
                    explanation=q_data.get("explanation"),
                    suggested_answer=q_data.get("suggested_answer"),
                    grading_criteria=q_data.get("grading_criteria")
                )
                
                # Parse options for MCQ
                if q_data.get("options"):
                    options = []
                    for opt_data in q_data["options"]:
                        options.append(MCQOption(
                            text=opt_data["text"],
                            is_correct=opt_data.get("is_correct", False)
                        ))
                    question.options = options
                
                questions.append(question)
                
            except Exception as e:
                logger.error(f"Error parsing question {i+1}: {str(e)}")
                continue
        
        return questions


class AIGrader:
    """AI-powered grading for theory questions"""
    
    def __init__(self):
        self.client = client
        self.model = DEFAULT_MODEL
    
    def grade_theory_answer(
        self,
        question_text: str,
        suggested_answer: str,
        student_answer: str,
        max_marks: float,
        grading_criteria: Optional[List[str]] = None
    ) -> tuple[float, str, float]:
        """
        Grade a theory answer using AI
        
        Returns:
            tuple: (marks_awarded, explanation, confidence_score)
        """
        try:
            prompt = self._create_grading_prompt(
                question_text, suggested_answer, student_answer,
                max_marks, grading_criteria
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced Nigerian secondary school teacher skilled in fair and accurate grading. Provide constructive feedback and accurate scoring."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent grading
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            grading_data = json.loads(response_text)
            
            marks_awarded = float(grading_data.get("marks_awarded", 0))
            explanation = grading_data.get("explanation", "")
            confidence = float(grading_data.get("confidence", 0.5))
            
            # Ensure marks don't exceed maximum
            marks_awarded = min(marks_awarded, max_marks)
            
            return marks_awarded, explanation, confidence
            
        except Exception as e:
            logger.error(f"Error grading theory answer: {str(e)}")
            # Return conservative grade on error
            return 0.0, f"Error in AI grading: {str(e)}", 0.0
    
    def _create_grading_prompt(
        self,
        question_text: str,
        suggested_answer: str,
        student_answer: str,
        max_marks: float,
        grading_criteria: Optional[List[str]] = None
    ) -> str:
        """Create grading prompt for AI"""
        
        prompt = f"""
Grade this theory question answer:

Question: {question_text}

Suggested Answer: {suggested_answer}

Student Answer: {student_answer}

Maximum Marks: {max_marks}

{f"Grading Criteria: {grading_criteria}" if grading_criteria else ""}

Instructions:
1. Compare student answer with suggested answer
2. Award marks based on correctness and completeness
3. Consider partial credit for partially correct answers
4. Be fair but maintain academic standards
5. Provide constructive feedback

Respond in JSON format:
{{
  "marks_awarded": 0.0,
  "explanation": "Detailed explanation of grading including what was correct/incorrect",
  "confidence": 0.85,
  "strengths": ["What the student did well"],
  "improvements": ["Areas for improvement"]
}}

Confidence scale: 0.0 (very uncertain) to 1.0 (very certain)
"""
        
        return prompt
    
    def grade_multiple_answers(
        self,
        grading_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Grade multiple theory answers in batch"""
        results = []
        
        for request in grading_requests:
            try:
                marks, explanation, confidence = self.grade_theory_answer(
                    request["question_text"],
                    request["suggested_answer"],
                    request["student_answer"],
                    request["max_marks"],
                    request.get("grading_criteria")
                )
                
                results.append({
                    "question_id": request.get("question_id"),
                    "marks_awarded": marks,
                    "explanation": explanation,
                    "confidence": confidence,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "question_id": request.get("question_id"),
                    "marks_awarded": 0.0,
                    "explanation": f"Grading error: {str(e)}",
                    "confidence": 0.0,
                    "success": False
                })
        
        return results


# Initialize global instances
quiz_generator = AIQuizGenerator()
ai_grader = AIGrader()


# Utility functions
def extract_keywords_from_text(text: str) -> List[str]:
    """Extract keywords from content text using AI"""
    try:
        prompt = f"""
Extract 5-10 key educational terms and concepts from this text:

{text[:2000]}

Return only a JSON array of keywords:
["keyword1", "keyword2", "keyword3"]

Focus on:
- Subject-specific terms
- Important concepts
- Topics covered
- Skills mentioned
"""
        
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at identifying key educational concepts and terms."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        keywords = json.loads(response.choices[0].message.content)
        return keywords if isinstance(keywords, list) else []
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []


def summarize_content(text: str, max_length: int = 500) -> str:
    """Summarize content text using AI"""
    try:
        prompt = f"""
Summarize this educational content in {max_length} characters or less:

{text[:2000]}

Focus on:
- Main topics covered
- Key concepts
- Learning objectives
- Important facts

Write in simple, clear language suitable for secondary school students.
"""
        
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating educational summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        summary = response.choices[0].message.content
        return summary[:max_length] if summary else ""
        
    except Exception as e:
        logger.error(f"Error summarizing content: {str(e)}")
        return text[:max_length] + "..." if len(text) > max_length else text
