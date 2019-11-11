import unittest

from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""

    def test_get_all_categories(self):
        res = self.client.get('/categories')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_get_all_categories_405(self):
        res = self.client.post('/categories')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json()['success'], False)

    def test_get_all_questions(self):
        res = self.client.get('/questions')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_post_new_questions(self):
        data = {
            "question": "test",
            "answer": "test",
            "difficulty": 1,
            "category": 1
        }
        res = self.client.post('/questions', json=data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()['success'], True)

    def test_post_new_question_400(self):
        data = {
            "question": "",
            "answer": "",
            "difficulty": 1,
            "category": 1
        }
        res = self.client.post('/questions', json=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['success'], False)

    def test_questions_category_404(self):
        res = self.client.get('/categories/4242323423/questions')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.get_json()['success'], False)

    def test_delete_question(self):
        # get id of last item in db, that's what we'll delete
        question_id = Question.query.all()[-1]
        res = self.client.delete(f'/questions/{question_id.id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_delete_question_404(self):
        res = self.client.delete('/questions/2031')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.get_json()['success'], False)

    def test_search_questions(self):
        data = {"searchTerm": "test"}
        res = self.client.post('/questions/results', json=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_search_questions_405(self):
        data = {"searchTerm": "test"}
        res = self.client.get('/questions/results', json=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json()['success'], False)

    def test_play_quiz(self):
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        res = self.client.post('/quizzes', json=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['success'], True)

    def test_play_quiz_405(self):
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        res = self.client.get('/quizzes', json=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json()['success'], False)

    def test_play_quiz_400(self):
        data = {
            "quiz_category": {
                "id": None
            },
            "previous_questions": []
        }
        res = self.client.post('/quizzes', json=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
