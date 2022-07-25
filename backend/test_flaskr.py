import os
#from socket import J1939_MAX_UNICAST_ADDR
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category
from settings import DATABASE_NAME_2, DATABASE_PORT, DATABASE_OWNER, DATABASE_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = f'postgresql://{DATABASE_OWNER}:{DATABASE_PASSWORD}@localhost:{DATABASE_PORT}/{DATABASE_NAME_2}'
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

#TEST FOR GET ALL CATEGORIES HANDLERS
    def test_get_categories(self):
        response = self.client().get('/api/v1/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['categories']['1'], 'Science')
        self.assertEqual(data['categories']['2'], 'Art')
        self.assertEqual(data['categories']['3'], 'Geography')
        self.assertEqual(data['categories']['4'], 'History')
        self.assertEqual(data['categories']['5'], 'Entertainment')
        self.assertEqual(data['categories']['6'], 'Sports')
        self.assertTrue(data['categories']['1'])
        self.assertTrue(data['categories']['2'])
        self.assertTrue(data['categories']['3'])
        self.assertTrue(data['categories']['4'])
        self.assertTrue(data['categories']['5'])
        self.assertTrue(data['categories']['6'])
        self.assertTrue(data['categories'])
        

#TEST FOR GET ALL QUESTIONS
    def test_get_questions(self):
        response = self.client().get('/api/v1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['categories']['1'], 'Science')
        self.assertEqual(data['categories']['2'], 'Art')
        self.assertEqual(data['categories']['3'], 'Geography')
        self.assertEqual(data['categories']['4'], 'History')
        self.assertEqual(data['categories']['5'], 'Entertainment')
        self.assertEqual(data['categories']['6'], 'Sports')
        self.assertTrue(data['categories']['1'])
        self.assertTrue(data['categories']['2'])
        self.assertTrue(data['categories']['3'])
        self.assertTrue(data['categories']['4'])
        self.assertTrue(data['categories']['5'])
        self.assertTrue(data['categories']['6'])
        self.assertTrue(data['categories'])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['questions'][0]['answer'])
        self.assertTrue(data['questions'][0]['category'])
        self.assertTrue(data['questions'][0]['difficulty'])
        self.assertTrue(data['questions'][0]['id'])
        self.assertTrue(data['questions'][0]['question'])
        self.assertTrue(data['questions'])


# #TEST FOR DELETE QUESTIONS
#     def test_delete_questions(self):
#         response = self.client().delete('/api/v1/questions/6')
#         data = json.loads(response.data)

#         question = Question.query.filter(Question.id == 6).one_or_none()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['success'], True)
#         self.assertEqual(data['deleted'], 6)
#         self.assertEqual(question, None)


#TEST FOR DELETE QUESTIONS THAT HAS ALREADY BEEN DELETED
    def test_delete_alreadydeleted_question(self):
        response = self.client().delete('/api/v1/questions/4')
        data = json.loads(response.data)


        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['status'], 'Already Deleted')
        self.assertEqual(data['error'], 400)
        self.assertFalse(data['success'])
        self.assertTrue(data['error'])
        self.assertTrue(data['status'])

        
# #TEST FOR POST QUESTIONS
    def test_post_questions(self):
        response = self.client().post('/api/v1/questions', json={"answer":"russia", "category":6, "difficulty":4, "question":"where is the fight happening"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])


 #TEST FOR POST QUESTIONS WITH EMPTY JSON PAYLOAD
    def test_post_questions(self):
        response = self.client().post('/api/v1/questions', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], "Bad Request")
        self.assertTrue(data['error'])
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])


#TEST FOR GET QUESTIONS WITH CATEGORIES
    def test_get_questions_by_questionid_and_categoryid(self):
        response = self.client().get('/api/v1/categories/2/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['questions'][0]['answer'])
        self.assertTrue(data['questions'][0]['category'])
        self.assertTrue(data['questions'][0]['difficulty'])
        self.assertTrue(data['questions'][0]['id'])
        self.assertTrue(data['questions'][0]['question'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])


#TEST FOR GET QUESTIONS WITH CATEGORIES WITH A CATEGORY THAT DOESNT EXIST
    def test_get_questions_by_invalid_categoryid(self):
        category = Category.query.order_by(Category.id.desc()).all()[0].format()['id']+10

        response = self.client().get(f'/api/v1/categories/{category}/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Not Found")
        self.assertTrue(data['error'])
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])


 #TEST FOR EVENT HANDLERS
    def test_400_bad_request(self):
        response = self.client().post('/api/v1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], "Bad Request")
        self.assertTrue(data['error'])
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])


    def test_404_not_found(self):
        response = self.client().get('/api/v1/question')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Not Found")
        self.assertTrue(data['error'])
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])



    def test_405_method_not_allowed(self):
        response = self.client().patch('/api/v1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "Method Not Allowed")
        self.assertTrue(data['error'])
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()