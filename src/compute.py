from flask import Blueprint, request
from flask.json import jsonify
import os
import uuid
import os
from skimage.metrics import structural_similarity
from skimage.transform import resize
import cv2
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR




sim = Blueprint("sim", __name__, url_prefix="/api/v1/sim")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
 

current_directory = os.getcwd()

image_folder = os.path.join(current_directory, 'images')
upload_folder = os.path.join(current_directory, 'uploads' )


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'uploads'  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def orb_sim(img1, img2):
    orb = cv2.ORB_create()

  
    kp_a, desc_a = orb.detectAndCompute(img1, None)
    kp_b, desc_b = orb.detectAndCompute(img2, None)


    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    

    matches = bf.match(desc_a, desc_b)
 
    similar_regions = [i for i in matches if i.distance < 70]  
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)

def structural_sim(img1, img2):
    sim, diff = structural_similarity(img1, img2, full=True, win_size=3, data_range=255)
    return sim

def crop_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) == 0:
        return None
    
    for (x, y, w, h) in faces:
        image[y:y+h, x:x+w] = 255 
    
    return image

def normalize_score(orb, ssim):
    if orb >= 7.0 and ssim >= 4.0:
        return round(min(100.0000, max(95.0000, 100 - (orb - 7) * 5)), 4) + ssim / 2
    elif orb >= 6.0 and ssim >= 4.0:
        return round(min(95.0000, max(90.0000, 95 - (orb - 6) * 5)), 4) + ssim / 2
    elif orb >= 5.0 and ssim >= 4.0:
        return round(min(90.0000, max(85.0000, 90 - (orb - 5) * 5)), 4) + ssim / 2
    elif orb >= 2.0 and ssim >= 4.0:
        return round(min(85.0000, max(80.0000, 85 - (orb - 2) * 5)), 4) + ssim / 2
    elif orb >= 2.0 and ssim >= 3.5:
        return round(min(80.0000, max(75.0000, 80 - (orb - 2) * 5)), 4) + ssim / 2
    elif orb >= 2.0 and ssim >= 3.0:
        return round(min(75.0000, max(70.0000, 75 - (orb - 2) * 5)), 4) + ssim / 2
    else:
        return round(max(0.0000, min(70.0000, 5 + (orb - 2) * 5)), 4) + ssim / 2

   



@sim.route('/classify', methods=['POST'])
def similarity():
    country = request.args.get('country')
    type = request.args.get('type')
    print(f'{country} {type}')
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'})

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected image'}), HTTP_204_NO_CONTENT

    if file and allowed_file(file.filename):
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]

        filename = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filename)

      
        id1_path = os.path.join(image_folder, 'id1.jpg')
        id2_path = os.path.join(image_folder, 'id5.jpg')
        id3_path = os.path.join(upload_folder, unique_filename)
        

        img1 = cv2.imread(id1_path, 0)
        img2 = cv2.imread(id3_path, 0)
        
        

        if img1 is not None and img2 is not None:

            img1_no_faces = crop_faces(cv2.imread(id1_path))
            img2_no_faces = crop_faces(cv2.imread(id3_path))
            if img2_no_faces is None: 
                return jsonify({ 'error': 'No face detected'})


            orb_similarity = orb_sim(img1_no_faces, img2_no_faces)
            print("Similarity using ORB between id1 and id2 (without faces) is:", orb_similarity)

            img2_no_faces = resize(img2_no_faces, img1_no_faces.shape, anti_aliasing=True, preserve_range=True)
            ssim = structural_sim(img1_no_faces, img2_no_faces)
            print("Similarity using SSIM between id1 and id2 (without faces) is:", ssim)
            confidence = normalize_score(orb_similarity*10, ssim*10)
            result = {'classification': f'{type}','country': f'{country}', 'confidence': confidence}, HTTP_200_OK
            
            return jsonify(result)
        
        else:
            return jsonify({'error': 'Error: One or both of the ID card images could not be loaded.'}), HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return jsonify({'error': 'error in image processing 2'}), HTTP_500_INTERNAL_SERVER_ERROR