"""
AI Service - Integration with OpenAI for content generation and educational assistance
"""

import openai
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered educational content generation"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    async def generate_study_plan(
        self, 
        subject: str, 
        grade_level: str, 
        learning_objectives: List[str],
        duration_weeks: int,
        student_performance: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive study plan"""
        try:
            # Prepare context for AI
            context = f"""
            Create a comprehensive {duration_weeks}-week study plan for:
            - Subject: {subject}
            - Grade Level: {grade_level}
            - Learning Objectives: {', '.join(learning_objectives)}
            """
            
            if student_performance:
                context += f"""
            - Student Performance Data: {json.dumps(student_performance, indent=2)}
            """
            
            prompt = f"""
            {context}
            
            Create a detailed study plan with the following structure:
            1. Overall plan title and description
            2. Weekly breakdown with topics and activities
            3. Learning milestones and assessments
            4. Recommended study time per week
            5. Prerequisites and resources needed
            
            Format the response as a JSON object with the following structure:
            {{
                "title": "Study Plan Title",
                "description": "Brief description of the plan",
                "total_weeks": {duration_weeks},
                "estimated_hours_per_week": 5,
                "weeks": [
                    {{
                        "week_number": 1,
                        "title": "Week 1 Title",
                        "topics": ["Topic 1", "Topic 2"],
                        "activities": ["Activity 1", "Activity 2"],
                        "learning_goals": ["Goal 1", "Goal 2"],
                        "assessment": "Assessment description"
                    }}
                ],
                "milestones": [
                    {{
                        "week": 2,
                        "title": "Milestone 1",
                        "description": "Description of milestone"
                    }}
                ],
                "resources": ["Resource 1", "Resource 2"],
                "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
            }}
            
            Ensure the content is appropriate for {grade_level} students and focuses on practical, engaging learning activities.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational curriculum designer specializing in African secondary education."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            try:
                plan_data = json.loads(content)
                return plan_data
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic structure
                return {
                    "title": f"{subject} Study Plan",
                    "description": f"A {duration_weeks}-week study plan for {subject}",
                    "total_weeks": duration_weeks,
                    "estimated_hours_per_week": 5,
                    "weeks": [
                        {
                            "week_number": i + 1,
                            "title": f"Week {i + 1}",
                            "topics": [f"Topic {i + 1}"],
                            "activities": [f"Activity {i + 1}"],
                            "learning_goals": [f"Goal {i + 1}"],
                            "assessment": f"Week {i + 1} assessment"
                        }
                        for i in range(duration_weeks)
                    ],
                    "milestones": [],
                    "resources": [],
                    "prerequisites": []
                }
                
        except Exception as e:
            logger.error(f"Error generating study plan: {str(e)}")
            raise
    
    async def generate_study_content(
        self, 
        topic: str, 
        keywords: List[str], 
        difficulty_level: str,
        content_type: str = 'text',
        grade_level: str = 'secondary'
    ) -> str:
        """Generate comprehensive study content for a topic"""
        try:
            prompt = f"""
            Create comprehensive study content for:
            - Topic: {topic}
            - Keywords: {', '.join(keywords)}
            - Difficulty Level: {difficulty_level}
            - Grade Level: {grade_level}
            - Content Type: {content_type}
            
            Structure the content as follows:
            1. Introduction and Overview
            2. Key Concepts and Definitions
            3. Detailed Explanation with Examples
            4. Real-world Applications
            5. Common Misconceptions
            6. Summary and Key Takeaways
            
            Make the content engaging, clear, and appropriate for {grade_level} students.
            Include practical examples relevant to African contexts where applicable.
            
            Length: Approximately 800-1200 words.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educator specializing in creating engaging educational content for African secondary school students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating study content: {str(e)}")
            raise
    
    async def generate_audio_script(
        self, 
        topic: str, 
        grade_level: str, 
        difficulty_level: str
    ) -> str:
        """Generate an audio script for text-to-speech"""
        try:
            prompt = f"""
            Create an engaging audio script for:
            - Topic: {topic}
            - Grade Level: {grade_level}
            - Difficulty Level: {difficulty_level}
            
            The script should be:
            1. Conversational and engaging
            2. Easy to understand when spoken
            3. Include natural pauses and emphasis
            4. Approximately 5-7 minutes when spoken
            5. Include interactive elements (questions for reflection)
            
            Format with natural speaking cues like:
            - [PAUSE] for brief pauses
            - [EMPHASIS] for emphasized words
            - [SLOW] for sections that should be spoken slowly
            
            Make it feel like a friendly tutor explaining the concept.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging audio educational content for students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating audio script: {str(e)}")
            raise
    
    async def generate_practice_questions(
        self, 
        topic: str, 
        grade_level: str, 
        difficulty_level: str,
        question_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate practice questions for a topic"""
        try:
            prompt = f"""
            Create {question_count} practice questions for:
            - Topic: {topic}
            - Grade Level: {grade_level}
            - Difficulty Level: {difficulty_level}
            
            Create a mix of question types:
            1. Multiple choice (4 options)
            2. True/False with explanation
            3. Short answer
            4. Problem-solving (if applicable)
            
            Format as JSON array with this structure:
            [
                {{
                    "question": "Question text",
                    "type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Explanation of why this is correct",
                    "difficulty": "medium",
                    "points": 1
                }}
            ]
            
            Ensure questions test understanding, not just memorization.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational assessments that test deep understanding."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            try:
                questions = json.loads(content)
                return questions
            except json.JSONDecodeError:
                # If JSON parsing fails, create basic questions
                return [
                    {
                        "question": f"What is the main concept of {topic}?",
                        "type": "short_answer",
                        "correct_answer": f"The main concept of {topic} is...",
                        "explanation": "This tests basic understanding of the topic",
                        "difficulty": difficulty_level,
                        "points": 1
                    }
                    for _ in range(question_count)
                ]
                
        except Exception as e:
            logger.error(f"Error generating practice questions: {str(e)}")
            raise
    
    async def extract_keywords(self, text: str) -> List[str]:
        """Extract key concepts and keywords from text"""
        try:
            prompt = f"""
            Extract the most important keywords and concepts from this text:
            "{text}"
            
            Return a JSON array of 5-10 keywords that represent the main concepts.
            Focus on educational terms, subject-specific vocabulary, and key concepts.
            
            Format: ["keyword1", "keyword2", "keyword3", ...]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying key educational concepts and terminology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            try:
                keywords = json.loads(content)
                return keywords
            except json.JSONDecodeError:
                # If JSON parsing fails, extract basic keywords
                words = text.split()
                return [word.strip('.,!?') for word in words if len(word) > 4][:10]
                
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    async def analyze_student_performance(
        self, 
        student_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze student performance and provide recommendations"""
        try:
            prompt = f"""
            Analyze this student performance data and provide insights:
            {json.dumps(student_data, indent=2)}
            
            Provide analysis in JSON format:
            {{
                "overall_performance": "excellent/good/average/needs_improvement",
                "strengths": ["strength1", "strength2"],
                "areas_for_improvement": ["area1", "area2"],
                "recommendations": ["recommendation1", "recommendation2"],
                "suggested_focus_areas": ["focus1", "focus2"],
                "learning_style_insights": "insights about learning preferences"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational analyst specializing in student performance assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            try:
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError:
                return {
                    "overall_performance": "average",
                    "strengths": [],
                    "areas_for_improvement": [],
                    "recommendations": [],
                    "suggested_focus_areas": [],
                    "learning_style_insights": "More data needed for detailed analysis"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing student performance: {str(e)}")
            raise
    
    async def generate_quiz_from_content(
        self, 
        content: str, 
        question_count: int = 10,
        difficulty_level: str = 'medium'
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions from provided content"""
        try:
            prompt = f"""
            Create {question_count} quiz questions based on this content:
            "{content}"
            
            Difficulty Level: {difficulty_level}
            
            Create a variety of question types and format as JSON:
            [
                {{
                    "question": "Question text",
                    "type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Explanation",
                    "difficulty": "{difficulty_level}",
                    "points": 1
                }}
            ]
            
            Ensure questions test comprehension of the provided content.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational quizzes from content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            try:
                questions = json.loads(content)
                return questions
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"Error generating quiz from content: {str(e)}")
            raise
