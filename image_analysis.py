"""
Image Analysis Module for AI Chatbot
تحليل الصور باستخدام الذكاء الاصطناعي
"""

import os
import traceback
import google.generativeai as genai

def configure_image_analysis(app, config):
    """Configure image analysis endpoints for the Flask app"""
    
    # Initialize Gemini Vision API
    gemini_available = False
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        vision_model = genai.GenerativeModel('gemini-pro-vision')
        gemini_available = True
        print("✅ Gemini Vision API initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Gemini Vision API: {e}")
        traceback.print_exc()
    
    @app.route('/analyze_image', methods=['POST'])
    def analyze_image():
        """Analyze an uploaded image using Gemini"""
        from flask import request, jsonify
        
        try:
            data = request.json
            image_url = data.get('image_url')
            question = data.get('question')
            conversation_id = data.get('conversation_id', '')
            
            if not image_url or not question:
                return jsonify({'error': 'Missing image_url or question'}), 400
            
            # Get the full path to the image
            image_path = os.path.join(os.getcwd(), image_url.lstrip('/'))
            
            if not os.path.exists(image_path):
                return jsonify({'error': f'Image not found at path: {image_path}'}), 404
            
            # Use Gemini to analyze the image
            if gemini_available:
                try:
                    # Load the image
                    image_parts = [
                        {
                            "mime_type": "image/jpeg",  # Adjust based on actual image type
                            "data": open(image_path, "rb").read()
                        }
                    ]
                    
                    # Create the prompt with the question
                    prompt = f"""أنا أرسلت لك صورة. {question}

I sent you an image. {question}

Please analyze the image and provide a detailed response in both Arabic and English."""
                    
                    # Generate the response
                    response = vision_model.generate_content([prompt, image_parts[0]])
                    
                    if response and response.text:
                        analysis = response.text.strip()
                        
                        # Record the question and answer in the conversation
                        if conversation_id:
                            from app import record_message
                            record_message(conversation_id, "user", question)
                            record_message(conversation_id, "assistant", analysis)
                        
                        return jsonify({
                            'success': True,
                            'analysis': analysis
                        })
                    else:
                        return jsonify({'error': 'Failed to analyze image'}), 500
                    
                except Exception as e:
                    print(f"Error analyzing image with Gemini: {e}")
                    traceback.print_exc()
                    return jsonify({'error': str(e)}), 500
            else:
                return jsonify({'error': 'Gemini Vision API not available'}), 503
                
        except Exception as e:
            print(f"Error in analyze_image: {e}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    return app
