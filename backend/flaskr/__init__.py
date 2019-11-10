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
            return jsonify({
                'question': question,
                'success': True
            }), 201
        except Exception as e:
            print(e)
            abort(e.code)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            questions = Question.query.filter(
                        Question.question.ilike(f"%{request.get_json()['searchTerm']}%")).all()
            formatted_questions = [
                question.format() for question in questions
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
                'total_questions': len(questions),
            }), 201
        except Exception as e:
            print(e)
            abort(e.code)

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            if not questions:
                abort(404)
            formatted_questions = [
                question.format() for question in questions
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
                'current_category': categories_dict[category_id],
                'total_questions': len(questions),
            })
        except Exception as e:
            print(e)
            abort(e.code)
            
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            category = request.get_json()['quiz_category']['id']
            category = int(category)
            if category == 0:
                questions = get_all_questions().get_json()
            else:
                questions = get_questions_by_category(category).get_json()
            previous_questions = request.get_json()['previous_questions']
            return jsonify({
                'quizCategory': 'ALL' if category == 0 else questions['categories'][str(category)],
                'categories': questions['categories'],
                'question': questions['questions'][len(previous_questions)]
                if len(questions['questions']) > len(previous_questions) else questions['questions'][0],
                'success': True
            })
        except Exception as e:
            print(e)
            abort(e.code)

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
