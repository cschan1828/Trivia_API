import os
from random import randint, choice

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

    # Set up CORS. Allow '*' for origins.
    cors = CORS(app, resources={r"/": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        '''
        Set Access-Control-Allow and CORS.
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')

        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        '''
        Endpoint for GET requests handling for all available categories.
        '''
        return jsonify({
            'categories': [c.type for c in Category.query.all()]
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        '''
        An endpoint to handle GET requests for questions including pagination.
        Return a list of questions, number of total questions,
        current category, categories and page.
        '''
        page_num = request.args.get('page', 1, type=int)
        questions = [q.format() for q in Question.query.all()]
        total_questions = len(questions)

        return jsonify({
            'questions': questions[
                (page_num - 1)
                * QUESTIONS_PER_PAGE:page_num
                * QUESTIONS_PER_PAGE
                ],
            'total_questions': total_questions,
            'categories': [c.type for c in Category.query.all()],
            'current_category': None,
            'page': page_num
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        '''
        Create an endpoint to DELETE a question using a question ID.
        '''
        try:
            target_question = Question.query.get(question_id)
            target_question.delete()
            return jsonify({
                'message': 'Delete question {question_id} successfully.'
                .format(question_id=question_id)
            })
        except Exception as e:
            print(e)
            return jsonify({
                'message': 'Not able to delete question {question_id}.'.format(
                    question_id=question_id
                )
            })

    @app.route('/questions', methods=['POST'])
    def create_question():
        '''
        Create an endpoint to POST a new question
        '''
        question_input = request.json
        if question_input:
            try:
                question_created = Question(
                    question=question_input['question'],
                    answer=question_input['answer'],
                    category=str(int(question_input['category']) + 1),
                    difficulty=question_input['difficulty']
                )
                question_created.insert()
                return jsonify({
                    'message': 'Create the new question successfully.'
                })
            except Exception as e:
                print(e)
                return jsonify({
                    'message': 'Not able to create the question.'
                })
        else:
            abort(400)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        '''
        Create a POST endpoint to get questions based on a search term.
        Return any questions for whom the search term is
        a substring of the question.
        '''
        search_term = request.json['searchTerm']
        if search_term:
            query_results = Question.query.filter(
                Question.question.ilike("%{term}%".format(term=search_term))
            ).all()
            return jsonify({'questions': [q.format() for q in query_results]})
        else:
            abort(400)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        '''
        Create a GET endpoint to get questions based on category.
        '''
        try:
            questions = [
                    q.format() for q in Question.query.filter(
                        Question.category == str(category_id)
                    ).all()
                ]
            current_category = Category.query.get(category_id).format()['type']
            return jsonify({
                'questions': questions,
                'current_category': current_category
            })
        except Exception as e:
            print(e)
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        '''
        Create a POST endpoint to get questions to play the quiz.
        '''
        response = request.json
        category_id = str(int(response['quiz_category']['id']) + 1)
        category_type = response['quiz_category']['type']
        previous_question_ids = response['previous_questions']

        if (category_id == '1') and (category_type == 'click'):
            questions = Question.query.all()
            random_num = randint(0, len(questions) - 1)

            return jsonify({
                'question': questions[random_num].format()
            })

        elif category_id:
            try:
                questions = Question.query.filter(
                    Question.category == category_id
                ).all()
                q_dict = dict(zip(
                                [q.id for q in questions],
                                list(range(len(questions)))
                ))

                if previous_question_ids:
                    for k in previous_question_ids:
                        del q_dict[k]

                    if q_dict:
                        random_num = q_dict[choice(list(q_dict))]
                    else:
                        random_num = 0

                else:
                    random_num = randint(0, len(questions) - 1)

                return jsonify({
                    'question': questions[random_num].format()
                })
            except Exception as e:
                print(e)
                abort(404)
        else:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        '''
        Error handlers for 404 Not Found Error.
        '''
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        '''
        Error handlers for 422 Unprocessable Entity Error.
        '''
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    return app
