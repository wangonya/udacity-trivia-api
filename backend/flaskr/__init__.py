import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def get_all_categories():
        try:
            categories = Category.query.all()
            formatted_categories = [
                category.format() for category in categories
            ]
            category_keys = []
            category_values = []

            for category in formatted_categories:
                category_keys.append(category['id'])
                category_values.append(category['type'])

            categories_dict = dict(zip(category_keys, category_values))
            return jsonify({
                'success': True,
                'categories': categories_dict
            })
        except Exception as e:
            print(e)
            abort(e.code)

    @app.route('/questions')
    def get_all_questions():
        try:
            questions = Question.query.paginate(1, QUESTIONS_PER_PAGE, False)
            # questions = Question.query.all()
            formatted_questions = [
                question.format() for question in questions.items
            ]
            categories = Category.query.all()
            formatted_categories = [
                category.format() for category in categories
            ]

            category_keys = []
            category_values = []

            for category in formatted_categories:
                category_keys.append(category['id'])
                category_values.append(category['type'])

            categories_dict = dict(zip(category_keys, category_values))

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'categories': categories_dict,
                'current_category': None,
                'total_questions': questions.total,
            })
        except Exception as e:
            print(e)
            abort(e.code)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if not question:
                abort(404)
            question.delete()
            return get_all_questions()
        except Exception as e:
            print(e)
            abort(e.code)

    @app.route('/questions', methods=['POST'])
    def post_new_question():
        try:
            question = request.get_json()
            for value in question.values():
                if not value:
                    abort(400)
            Question(
                question=question['question'],
                answer=question['answer'],
                category=question['category'],
                difficulty=question['difficulty']
            ).insert()
            return jsonify(question), 201
        except Exception as e:
            print(e)
            abort(e.code)
    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unable to process request'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    return app
