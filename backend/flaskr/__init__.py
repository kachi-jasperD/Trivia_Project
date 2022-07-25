from crypt import methods
from importlib.resources import path
from ntpath import join
import os
from select import select
import sqlite3
from sre_parse import CATEGORIES
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category




def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.postgresql')
    )
    setup_db(app)

    QUESTIONS_PER_PAGE = 10

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int) 
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        formatted_questions= [question.format() for question in selection]
        current_question = formatted_questions[start:end]

        return current_question

    def categories():
        categories = Category.query.all()

        cat = {str(cat.id) : str(cat.type) for cat in categories}

        return cat
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    #GET ALL CATEGORIES
    @app.route('/api/v1/categories')
    #@cross_origin()
    def get_categories():
           
        if len(categories()) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories' : categories()
            })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/api/v1/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        #selection = Question.query.filter().all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success' : True,
            'questions' : current_questions,
            'totalQuestions' : len(Question.query.all()),
            'categories': categories()
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/api/v1/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
            
            question.delete()

            return jsonify({
                'success' : True,
                'deleted' : question.id
            })

        except:
            return jsonify({
                'success' : False,
                'error' : 400,
                'status' : "Already Deleted"
            })



    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/api/v1/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        if 'searchTerm' not in body:
            try:
                new_answer = request.get_json()['answer']
                new_category = request.get_json()['category']
                new_difficulty = request.get_json()['difficulty']
                new_question = request.get_json()['question']
    
            except:
                abort(400)
            print(new_answer, new_category, new_difficulty,new_question)
                
            try:
                question = Question(answer=new_answer, category=new_category, difficulty=new_difficulty, question=new_question)
                question.insert()

                return jsonify({
                        'success' : True,
                        'created' : question.id,
                    })
                
            except:
                abort(422)
            """
            @TODO:
            Create a POST endpoint to get questions based on a search term.
            It should return any questions for whom the search term
            is a substring of the question.

            TEST: Search by any phrase. The questions list will update to include
            only question that include that string within their question.
            Try using the word "title" to start.
            """
        elif 'searchTerm' in body:
            if body["searchTerm"] == '':
                abort(422)
            try:
                questions = Question.query.filter(Question.question.ilike(f'%{body["searchTerm"]}%')).all()

                if not questions:
                    abort(404)

                current_questions = paginate_questions(request, questions)

                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions": len(questions),
                    "current_category": 0
                })
            except:
                abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    #GET QUESTIONS BY CATEGORY ID
    @app.route('/api/v1/categories/<int:category_id>/questions')
    def get_category_by_id(category_id):
        questions  = Question.query.filter(Question.category == str(category_id)).all()

        if len(questions) == 0:
            abort(404)

        if questions is None:
            abort(404)

        else:
            return jsonify({
                'success' : True,
                'questions' : [question.format() for question in questions],
                'totalQuestions': len(questions),
                'current_category': category_id
            })



    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/api/v1/quizzes', methods=['POST'])
    def play():
        try:
            body = request.get_json()
            category = body.get('quiz_category', None)
            category_id = None
            if category is not None:
                category_id = category['id']
            
            incoming_questions = body.get('previous_questions', None)
            if category_id is None or incoming_questions is None:
                abort(404)

            questions = Question.query.filter(
                Question.category == category_id)
                

            if category_id != 0 and questions.count() <= len(incoming_questions):
                return jsonify({
                    "success": True,
                    "question": {},
                })

            id_limit = Question.query.order_by(
                Question.id.desc()).first().format()['id'] + 1

            random_question = None
            while random_question is None or random_question.format()['id'] in incoming_questions:
                random_id = random.randrange(1, id_limit)
                random_question = Question.query.get(random_id) if category_id == 0 else Question.query.filter(
                    Question.id == random_id, Question.category == category_id).first()

            return jsonify({
                "success": True,
                "question": random_question.format(),
            })
        except:
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    #ERROR HANDLERS
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success" : False,
            "error" : 400,
            "message" : "Bad Request"
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success" : False,
            "error" : 401,
            "message" : "Unauthorized"
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success" : False,
            "error" : 403,
            "message" : "Forbidden"
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success" : False,
            "error" : 404,
            "message" : "Not Found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success" : False,
            "error" : 405,
            "message" : "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success" : False,
            "error" : 422,
            "message" : "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success" : False,
            "error" : 500,
            "message" : "Internal Server Error"
        }), 500
    
    
    return app

# if test_config is None:
#     app.config.from_pyfile('config.py', silent=True)

