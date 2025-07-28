"""
Quiz Grading Utility
Automated quiz grading system with intelligent feedback
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from ..database import get_db
from ..models.content_models import Quiz, Question, QuizSubmission
from ..models.progress_models import QuizProgress
from ..utils.cache import cache_result, invalidate_cache_pattern

import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_question_score(question: Question, user_answer: Any) -> Dict[str, Any]:
    """
    Calculate score for a single question based on type and answer
    """
    try:
        correct_answer = question.correct_answer
        points = question.points
        
        if question.question_type == "multiple_choice":
            # Handle multiple choice questions
            if isinstance(user_answer, str):
                is_correct = user_answer.lower() == str(correct_answer).lower()
            elif isinstance(user_answer, list):
                # Multiple select
                if isinstance(correct_answer, list):
                    is_correct = set(user_answer) == set(correct_answer)
                else:
                    is_correct = len(user_answer) == 1 and user_answer[0] == correct_answer
            else:
                is_correct = user_answer == correct_answer
            
            score = points if is_correct else 0
            
        elif question.question_type == "true_false":
            # Handle true/false questions
            user_bool = str(user_answer).lower() in ['true', '1', 'yes', 't']
            correct_bool = str(correct_answer).lower() in ['true', '1', 'yes', 't']
            is_correct = user_bool == correct_bool
            score = points if is_correct else 0
            
        elif question.question_type == "short_answer":
            # Handle short answer questions with flexible matching
            if not user_answer or not correct_answer:
                is_correct = False
                score = 0
            else:
                user_text = str(user_answer).strip().lower()
                correct_text = str(correct_answer).strip().lower()
                
                # Exact match
                if user_text == correct_text:
                    is_correct = True
                    score = points
                # Partial match (for keywords)
                elif len(correct_text.split()) > 1:
                    correct_words = set(correct_text.split())
                    user_words = set(user_text.split())
                    match_ratio = len(correct_words.intersection(user_words)) / len(correct_words)
                    
                    if match_ratio >= 0.8:  # 80% keyword match
                        is_correct = True
                        score = points
                    elif match_ratio >= 0.5:  # 50% keyword match - partial credit
                        is_correct = False
                        score = points * 0.5
                    else:
                        is_correct = False
                        score = 0
                else:
                    is_correct = False
                    score = 0
                    
        elif question.question_type == "essay":
            # Essay questions need manual grading or AI assistance
            # For now, give full points and mark for manual review
            is_correct = True  # Assume correct until manually reviewed
            score = points
            
        elif question.question_type == "fill_blank":
            # Handle fill in the blank questions
            if isinstance(correct_answer, list) and isinstance(user_answer, list):
                # Multiple blanks
                if len(user_answer) != len(correct_answer):
                    is_correct = False
                    score = 0
                else:
                    correct_count = 0
                    for i, (user_blank, correct_blank) in enumerate(zip(user_answer, correct_answer)):
                        if str(user_blank).strip().lower() == str(correct_blank).strip().lower():
                            correct_count += 1
                    
                    if correct_count == len(correct_answer):
                        is_correct = True
                        score = points
                    else:
                        is_correct = False
                        # Partial credit based on correct blanks
                        score = points * (correct_count / len(correct_answer))
            else:
                # Single blank
                user_text = str(user_answer).strip().lower()
                correct_text = str(correct_answer).strip().lower()
                is_correct = user_text == correct_text
                score = points if is_correct else 0
                
        elif question.question_type == "matching":
            # Handle matching questions
            if isinstance(user_answer, dict) and isinstance(correct_answer, dict):
                correct_matches = 0
                total_matches = len(correct_answer)
                
                for key, correct_value in correct_answer.items():
                    if key in user_answer and user_answer[key] == correct_value:
                        correct_matches += 1
                
                if correct_matches == total_matches:
                    is_correct = True
                    score = points
                else:
                    is_correct = False
                    # Partial credit based on correct matches
                    score = points * (correct_matches / total_matches)
            else:
                is_correct = False
                score = 0
                
        elif question.question_type == "ordering":
            # Handle ordering questions
            if isinstance(user_answer, list) and isinstance(correct_answer, list):
                is_correct = user_answer == correct_answer
                if is_correct:
                    score = points
                else:
                    # Partial credit for partially correct ordering
                    correct_positions = 0
                    min_length = min(len(user_answer), len(correct_answer))
                    
                    for i in range(min_length):
                        if user_answer[i] == correct_answer[i]:
                            correct_positions += 1
                    
                    score = points * (correct_positions / len(correct_answer))
            else:
                is_correct = False
                score = 0
                
        else:
            # Unknown question type
            logger.warning(f"Unknown question type: {question.question_type}")
            is_correct = False
            score = 0
        
        return {
            "is_correct": is_correct,
            "score": round(score, 2),
            "max_score": points,
            "explanation": question.explanation
        }
        
    except Exception as e:
        logger.error(f"Error calculating score for question {question.id}: {e}")
        return {
            "is_correct": False,
            "score": 0,
            "max_score": question.points,
            "explanation": "Error in grading",
            "error": str(e)
        }


def generate_detailed_feedback(
    quiz: Quiz,
    questions: List[Question],
    user_answers: Dict[str, Any],
    results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate detailed feedback for the quiz submission
    """
    try:
        total_score = sum(result["score"] for result in results)
        max_score = sum(result["max_score"] for result in results)
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        is_passed = percentage >= quiz.passing_score
        
        # Categorize performance
        if percentage >= 90:
            performance_level = "Excellent"
            performance_message = "Outstanding performance! You have mastered this material."
        elif percentage >= 80:
            performance_level = "Good"
            performance_message = "Good work! You have a solid understanding of the material."
        elif percentage >= 70:
            performance_level = "Satisfactory"
            performance_message = "Satisfactory performance. Consider reviewing the areas where you missed questions."
        elif percentage >= 60:
            performance_level = "Needs Improvement"
            performance_message = "You may need to review the material more thoroughly before retaking."
        else:
            performance_level = "Poor"
            performance_message = "Please review the course material carefully and consider additional study resources."
        
        # Analyze question types performance
        question_type_stats = {}
        for i, question in enumerate(questions):
            q_type = question.question_type
            if q_type not in question_type_stats:
                question_type_stats[q_type] = {"correct": 0, "total": 0, "score": 0, "max_score": 0}
            
            question_type_stats[q_type]["total"] += 1
            question_type_stats[q_type]["max_score"] += results[i]["max_score"]
            question_type_stats[q_type]["score"] += results[i]["score"]
            if results[i]["is_correct"]:
                question_type_stats[q_type]["correct"] += 1
        
        # Generate recommendations
        recommendations = []
        for q_type, stats in question_type_stats.items():
            accuracy = (stats["correct"] / stats["total"]) * 100
            if accuracy < 70:
                recommendations.append(
                    f"Focus on improving {q_type.replace('_', ' ')} questions (Current: {accuracy:.1f}%)"
                )
        
        # Identify weak areas (incorrect questions)
        weak_areas = []
        for i, (question, result) in enumerate(zip(questions, results)):
            if not result["is_correct"]:
                weak_areas.append({
                    "question_id": question.id,
                    "question_text": question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
                    "difficulty": question.difficulty,
                    "tags": question.tags or []
                })
        
        return {
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "is_passed": is_passed,
            "performance_level": performance_level,
            "performance_message": performance_message,
            "question_type_stats": question_type_stats,
            "recommendations": recommendations,
            "weak_areas": weak_areas[:5],  # Limit to top 5 weak areas
            "study_suggestions": generate_study_suggestions(weak_areas, question_type_stats)
        }
        
    except Exception as e:
        logger.error(f"Error generating feedback: {e}")
        return {
            "total_score": 0,
            "max_score": 0,
            "percentage": 0,
            "is_passed": False,
            "performance_level": "Error",
            "performance_message": "Error generating feedback",
            "error": str(e)
        }


def generate_study_suggestions(weak_areas: List[Dict], question_type_stats: Dict) -> List[str]:
    """
    Generate study suggestions based on performance
    """
    suggestions = []
    
    # Suggestions based on weak question types
    for q_type, stats in question_type_stats.items():
        accuracy = (stats["correct"] / stats["total"]) * 100
        if accuracy < 50:
            type_suggestions = {
                "multiple_choice": "Practice identifying key concepts and eliminating incorrect options",
                "true_false": "Focus on understanding absolute vs. conditional statements",
                "short_answer": "Review key terminology and practice concise explanations",
                "essay": "Work on structuring your thoughts and providing comprehensive answers",
                "fill_blank": "Study key terms and their definitions",
                "matching": "Review relationships between concepts and terms",
                "ordering": "Practice sequencing and understanding process flows"
            }
            if q_type in type_suggestions:
                suggestions.append(type_suggestions[q_type])
    
    # Suggestions based on difficulty levels of missed questions
    difficulties = [area.get("difficulty", "intermediate") for area in weak_areas]
    if "easy" in difficulties:
        suggestions.append("Review fundamental concepts - you're missing some basic questions")
    if "hard" in difficulties:
        suggestions.append("Challenge yourself with advanced practice problems")
    
    # Suggestions based on tags/topics
    all_tags = []
    for area in weak_areas:
        all_tags.extend(area.get("tags", []))
    
    if all_tags:
        from collections import Counter
        common_tags = Counter(all_tags).most_common(3)
        for tag, count in common_tags:
            if count > 1:
                suggestions.append(f"Focus additional study time on: {tag}")
    
    return suggestions[:5]  # Limit to top 5 suggestions


async def grade_quiz_submission(submission_id: int, quiz_id: int, user_answers: Dict[str, Any]):
    """
    Grade a quiz submission and update the database
    """
    db = next(get_db())
    
    try:
        # Get submission
        submission = db.query(QuizSubmission).filter(
            QuizSubmission.id == submission_id
        ).first()
        
        if not submission:
            logger.error(f"Submission {submission_id} not found")
            return
        
        # Get quiz and questions
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            logger.error(f"Quiz {quiz_id} not found")
            return
        
        questions = db.query(Question).filter(
            Question.quiz_id == quiz_id,
            Question.is_active == True
        ).order_by(Question.order_index).all()
        
        if not questions:
            logger.error(f"No questions found for quiz {quiz_id}")
            return
        
        # Grade each question
        results = []
        for question in questions:
            question_id_str = str(question.id)
            user_answer = user_answers.get(question_id_str)
            
            result = calculate_question_score(question, user_answer)
            results.append(result)
        
        # Generate feedback
        feedback = generate_detailed_feedback(quiz, questions, user_answers, results)
        
        # Update submission
        submission.score = feedback["total_score"]
        submission.max_score = feedback["max_score"]
        submission.percentage = feedback["percentage"]
        submission.is_passed = feedback["is_passed"]
        submission.feedback = feedback
        submission.question_results = results
        submission.graded_at = datetime.utcnow()
        
        # Update or create quiz progress
        progress = db.query(QuizProgress).filter(
            QuizProgress.user_id == submission.user_id,
            QuizProgress.quiz_id == quiz_id
        ).first()
        
        if not progress:
            progress = QuizProgress(
                user_id=submission.user_id,
                quiz_id=quiz_id,
                course_id=quiz.course_id,
                status="completed",
                score=submission.score,
                max_score=submission.max_score,
                is_passed=submission.is_passed,
                attempts=1,
                time_spent=submission.time_taken,
                completed_at=submission.submitted_at
            )
            db.add(progress)
        else:
            # Update existing progress if this is a better score
            if submission.score > progress.score:
                progress.score = submission.score
                progress.is_passed = submission.is_passed
                progress.completed_at = submission.submitted_at
            
            progress.attempts += 1
            progress.time_spent = (progress.time_spent or 0) + (submission.time_taken or 0)
        
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quiz:{quiz_id}:*")
        invalidate_cache_pattern(f"user:{submission.user_id}:progress:*")
        
        logger.info(f"Graded submission {submission_id} - Score: {submission.score}/{submission.max_score} ({submission.percentage:.1f}%)")
        
    except Exception as e:
        logger.error(f"Error grading submission {submission_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()
