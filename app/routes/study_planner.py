from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.models.study_plan import StudyPlan, StudyTask
from app import db
from openai import OpenAI
from datetime import datetime, timedelta
import json
import logging
import os

bp = Blueprint('study_planner', __name__)

@bp.route('/create_plan', methods=['GET', 'POST'])
@login_required
def create_plan():
    if request.method == 'POST':
        subject = request.form.get('subject')
        description = request.form.get('description')
        
        try:
            # Get API key from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found in environment variables")
            
            # Initialize OpenAI client with explicit API key
            client = OpenAI(api_key=api_key,http_client=None, base_url="https://api.openai.com/v1")
            
            # Print debug information
            print(f"Using API key: {api_key[:10]}...")  # Only print first 10 chars for security
            
            # Create a study plan using OpenAI
            prompt = f"""Create a detailed study plan for {subject}. Context: {description}
            Create a structured plan with the following:
            1. Main topics to cover
            2. Breakdown of topics into smaller sections
            3. Recommended study schedule or hours recommended per day
            4. Learning objectives or goals
            5. Practice exercises or activities
            
            The response must be valid JSON with this exact structure:
            {{
                "title": "Study Plan for {subject}",
                "tasks": [
                    {{
                        "title": "string",
                        "description": "string",
                        "due_date": "YYYY-MM-DD"
                    }}
                ]
                
            }}"""
            
            try:
                print("Attempting to call OpenAI API...")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using GPT-3.5 for better availability
                    messages=[
                        {"role": "system", "content": "You are a professional study planner and always return valid JSON that is well formatted and you also recommend resources for each topic."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={ "type": "json_object" }
                )
                print("Successfully received response from OpenAI")
                
                # Get the response content
                content = response.choices[0].message.content
                print(f"OpenAI Response: {content}")  # Debug print
                
                plan_data = json.loads(content)
                
                # Validate the plan data structure
                if not isinstance(plan_data, dict) or 'title' not in plan_data or 'tasks' not in plan_data:
                    raise ValueError("Invalid plan data structure")
                
                # Create study plan in database
                study_plan = StudyPlan(
                    title=plan_data['title'],
                    subject=subject,
                    description=description,
                    user_id=current_user.id
                )
                db.session.add(study_plan)
                db.session.commit()
                
                # Calculate dates starting from today
                start_date = datetime.now()
                
                # Add tasks to the study plan
                for i, task_data in enumerate(plan_data['tasks']):
                    # Set due date to be sequential days from today
                    due_date = start_date + timedelta(days=i+1)
                    task = StudyTask(
                        title=task_data['title'],
                        description=task_data['description'],
                        due_date=due_date,
                        study_plan_id=study_plan.id
                    )
                    db.session.add(task)
                
                db.session.commit()
                flash('Study plan created successfully!')
                return redirect(url_for('study_planner.view_plan', plan_id=study_plan.id))
                
            except Exception as api_error:
                print(f"OpenAI API error: {str(api_error)}")
                raise
            
        except Exception as e:
            print(f"Error creating study plan: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            db.session.rollback()
            flash('Error creating study plan. Please try again.')
            return redirect(url_for('study_planner.create_plan'))
            
    return render_template('study_planner/create_plan.html')

@bp.route('/plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        flash('Access denied.')
        return redirect(url_for('main.dashboard'))
    return render_template('study_planner/view_plan.html', plan=plan)

@bp.route('/plans')
@login_required
def list_plans():
    plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
    return render_template('study_planner/list_plans.html', plans=plans)

@bp.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = StudyTask.query.get_or_404(task_id)
    if task.study_plan.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    task.completed = not task.completed
    db.session.commit()
    return jsonify({'completed': task.completed}) 