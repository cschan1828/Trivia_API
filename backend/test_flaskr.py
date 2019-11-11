import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from random import choice

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
                             'postgres:aria1828@localhost:5432',
                             self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_json['categories']), 6)

    def test_create_question(self):
        res = self.client().post('/questions', json={
            'question': 'La Giaconda is better known as what?',
            'answer': 'Mona Lisa',
            'category': 2,
            'difficulty': 3
        })
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['message'],
                         'Create the new question successfully.')

    def test_search_question(self):
        res = self.client().post('/questions/search',
                                 json={'searchTerm':
                                       'La Giaconda is better known as what?'})
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['questions'][0]['answer'], 'Mona Lisa')
        self.assertEqual(response_json['questions'][0]['difficulty'], 3)

    def test_get_questions_by_category(self):
        '''
        Test getting questions that the category exists.
        '''
        res = self.client().get('/categories/5/questions')
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['current_category'], 'Entertainment')

    def test_get_questions_by_category_fail(self):
        '''
        Test getting questions that the category doesn't exit.
        '''
        res = self.client().get('/categories/95/questions')
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_delete_questions(self):
        target_question_id = choice([q.id for q in Question.query.all()])
        res = self.client().delete(
            '/questions/{id}'.format(id=target_question_id)
        )
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['message'],
                         'Delete question {id} successfully.'
                         .format(id=target_question_id))

    def test_delete_questions_fail(self):
        res = self.client().delete('/questions/105')
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['message'],
                         'Not able to delete question 105.')

    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={
            'quiz_category': {'type': 'Geography', 'id': 2},
            'previous_questions': []
        })
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_play_quiz_fail(self):
        res = self.client().post('/quizzes', json={
            'quiz_category': {'type': 'Unexisted', 'id': 50},
            'previous_questions': []
        })
        response_json = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_resource_not_found(self):
        res = self.client().get('/empty')
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
