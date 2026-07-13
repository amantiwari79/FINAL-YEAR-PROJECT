from django.test import TestCase
from unittest.mock import patch, MagicMock
from ai_engine.utils import (
    calculate_ats_score,
    rewrite_bullet_points,
    generate_cover_letter,
    career_coach_chat,
    generate_interview_questions,
    parse_resume_with_ai
)

class AIToolsHeuristicTestCase(TestCase):
    """
    Tests the fallback heuristic behaviors when no Gemini API key is configured.
    """
    def setUp(self):
        # Force get_gemini_client to return None
        self.patcher = patch('ai_engine.utils.get_gemini_client', return_value=None)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_parse_resume_with_ai_fallback(self):
        text = "Jane Doe\njane@example.com\n555-0199\nPython, Django developer."
        res = parse_resume_with_ai(text)
        self.assertEqual(res["name"], "Jane Doe")
        self.assertEqual(res["email"], "jane@example.com")
        self.assertIn("Python", res["skills"])

    def test_calculate_ats_score_fallback(self):
        resume_text = "Experienced Django and Python engineer."
        job_desc = "Looking for a Python developer with Django knowledge."
        score, feedback = calculate_ats_score(resume_text, job_desc)
        self.assertGreaterEqual(score, 60)
        self.assertIn("overall_assessment", feedback)
        self.assertIn("missing_keywords", feedback)

    def test_rewrite_bullet_points_fallback(self):
        bullets = ["Wrote Django views.", "Fixed SQL queries."]
        res = rewrite_bullet_points(bullets)
        self.assertTrue(len(res) > 0)
        self.assertIn("improved", res[0])
        self.assertIn("reason", res[0])

    def test_generate_cover_letter_fallback(self):
        res = generate_cover_letter("My resume", "Software Engineer", "Google", "Job desc")
        self.assertIn("Google", res)
        self.assertIn("Software Engineer", res)

    def test_career_coach_chat_fallback(self):
        history = [{"role": "user", "content": "hello"}]
        res = career_coach_chat(history, "how to improve?")
        self.assertIn("Career Coach", res)

    def test_generate_interview_questions_fallback(self):
        res = generate_interview_questions("My resume", "Job desc")
        self.assertIn("questions", res)
        self.assertEqual(len(res["questions"]), 3)


class AIToolsAPITestCase(TestCase):
    """
    Tests the client API integration pathways using mocks to simulate Gemini responses.
    """
    @patch('ai_engine.utils.get_gemini_client')
    def test_parse_resume_with_ai_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock Response structure for gemini-2.5-flash
        mock_response = MagicMock()
        mock_response.text = '{"name": "Alice Smith", "email": "alice@example.com", "skills": ["Python", "AWS"]}'
        mock_client.models.generate_content.return_value = mock_response
        
        res = parse_resume_with_ai("Alice Smith email: alice@example.com skills: Python AWS")
        mock_client.models.generate_content.assert_called_once()
        self.assertEqual(res["name"], "Alice Smith")
        self.assertIn("AWS", res["skills"])

    @patch('ai_engine.utils.get_gemini_client')
    def test_calculate_ats_score_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = '{"score": 85, "overall_assessment": "Excellent match.", "matching_skills": ["Django"], "missing_keywords": ["Kubernetes"], "suggestions": ["Learn Kubernetes"]}'
        mock_client.models.generate_content.return_value = mock_response
        
        score, feedback = calculate_ats_score("My resume text", "Job desc")
        self.assertEqual(score, 85)
        self.assertEqual(feedback["overall_assessment"], "Excellent match.")
        self.assertIn("Kubernetes", feedback["missing_keywords"])

    @patch('ai_engine.utils.get_gemini_client')
    def test_rewrite_bullet_points_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = '{"results": [{"original": "Wrote code.", "improved": "Architected clean modules.", "reason": "Better description."}]}'
        mock_client.models.generate_content.return_value = mock_response
        
        res = rewrite_bullet_points(["Wrote code."])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["improved"], "Architected clean modules.")

    @patch('ai_engine.utils.get_gemini_client')
    def test_generate_cover_letter_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "Mocked cover letter body."
        mock_client.models.generate_content.return_value = mock_response
        
        res = generate_cover_letter("Resume text", "Engineer", "Apple", "Job desc")
        self.assertEqual(res, "Mocked cover letter body.")

    @patch('ai_engine.utils.get_gemini_client')
    def test_career_coach_chat_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "Coach advice details."
        mock_client.models.generate_content.return_value = mock_response
        
        res = career_coach_chat([], "How to negotiate salary?")
        self.assertEqual(res, "Coach advice details.")

    @patch('ai_engine.utils.get_gemini_client')
    def test_generate_interview_questions_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = '{"questions": [{"type": "Technical", "question": "Explain MVC.", "tips": "Be concise."}]}'
        mock_client.models.generate_content.return_value = mock_response
        
        res = generate_interview_questions("Resume text", "Job desc")
        self.assertIn("questions", res)
        self.assertEqual(res["questions"][0]["question"], "Explain MVC.")

    def test_safe_json_loads_markdown_strip(self):
        from ai_engine.utils import safe_json_loads
        raw_response = "```json\n{\"test\": \"value\"}\n```"
        res = safe_json_loads(raw_response)
        self.assertEqual(res, {"test": "value"})

        raw_response_no_lang = "```\n{\"test2\": \"value2\"}\n```"
        res2 = safe_json_loads(raw_response_no_lang)
        self.assertEqual(res2, {"test2": "value2"})

    @patch('ai_engine.utils.get_gemini_client')
    def test_api_failure_fallback_recovery(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Simulate API Exception (e.g. Quota Exceeded / Client Error)
        mock_client.models.generate_content.side_effect = Exception("Quota Exceeded")
        
        # All tools should automatically fall back to mock heuristical outputs instead of returning error dicts
        res_parse = parse_resume_with_ai("Candidate text")
        self.assertEqual(res_parse["name"], "Candidate text")

        score, feedback = calculate_ats_score("Candidate text", "Job desc")
        self.assertEqual(score, 65)

        res_bullets = rewrite_bullet_points(["Wrote code."])
        self.assertEqual(res_bullets[0]["original"], "Wrote code.")

        res_letter = generate_cover_letter("Candidate text", "Engineer", "Apple", "Job desc")
        self.assertIn("Apple", res_letter)

        res_questions = generate_interview_questions("Candidate text", "Job desc")
        self.assertEqual(len(res_questions["questions"]), 3)
