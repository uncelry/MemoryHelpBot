import time
from tqdm import tqdm
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials
import cv2
import os


ENDPOINT = "https://testcvbn-prediction.cognitiveservices.azure.com/"
# Replace with a valid key
training_key = "56ae485f8fbe41969b2d52a6935d8b17"
prediction_key = "8dda2562bfd74bfabd2501490f7c20c0"
prediction_resource_id = "b9cba7ae-d1ff-4670-975e-c98aa96fb40a"
project_id = "a7aff6e2-2eee-4a72-bcef-e3cc9fac27d8"
path_pics = "C:/Users/UNCELRY/PycharmProjects/Lab1/PY_ANDROID/bot_videos_tmp/"  # путь где будут временно хранится фотки из видео
tags = []


def video_to_neiroset(tagName, path_video):
    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

    # Make tags in the project
    if tagName not in tags:
        new_tag = trainer.create_tag(project_id, tagName)
        # выделение из видео
        vidcap = cv2.VideoCapture(path_video)

        total_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
        print(total_frames)
        n = int(total_frames - 3)
        success, image0 = vidcap.read()
        cv2.imwrite(path_pics + "test.jpg", image0)

        try:
            # загрузка в сеть
            for image_num in tqdm(range(0, n)):
                success, image = vidcap.read()
                try:
                    cv2.imwrite(path_pics + "frame%d.jpg" % image_num, image)
                except Exception as e:
                    print("Ошибка чтения кадра. Пропускаем...")
                    continue
                with open(path_pics + "frame%d.jpg" % image_num, "rb") as image_contents:
                    print(path_pics + "frame%d.jpg" % image_num)
                    trainer.create_images_from_data(project_id, image_contents.read(), tag_ids=[new_tag.id])
            vidcap.release()

            # обучение сетки
            iteration = trainer.train_project(project_id)
            while iteration.status != "Completed":
                iteration = trainer.get_iteration(project_id, iteration.id)
                print("Training status: " + iteration.status)
                time.sleep(1)

            # публикация сетки
            publish_iteration_name = iteration.name
            trainer.update_iteration(project_id, iteration.id, publish_iteration_name, is_default=True)
            trainer.publish_iteration(project_id, iteration.id, publish_iteration_name,
                                      '/subscriptions/b9cba7ae-d1ff-4670-975e-c98aa96fb40a/resourceGroups/TestCustVisBN'
                                      '/providers/Microsoft.CognitiveServices/accounts/testCVBN-Prediction')
            #  тестируем новую итерацию
            test_seti = prediction(path_pics + "test.jpg", publish_iteration_name)
            for pred in test_seti.predictions:
                if pred.probability * 100 >= 0:
                    print("Done!")
                    break
                else:
                    print("Необходимо другое видео!")
                    trainer.unpublish_iteration(project_id, iteration.id)
                    trainer.delete_iteration(project_id, iteration.id)
            return publish_iteration_name
        except Exception as e:
            print("Ошибочка:")
            print(e)
            trainer.delete_tag(project_id, new_tag.id)
            while True:
                img_list = trainer.get_untagged_images(project_id)
                if len(img_list) == 0:
                    break
                img_id_list = list()
                for img in img_list:
                    img_id_list.append(img.id)
                trainer.delete_images(project_id, img_id_list)
                print("Deleted")
            # trainer.unpublish_iteration(project_id, iteration.id)
            # trainer.delete_iteration(project_id, iteration.id)

            return "err"
    else:
        print('такой тэг уже есть')


def prediction(path_img, pubitername):
    prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
    predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

    with open(path_img, "rb") as image_contents:
        results = predictor.classify_image(project_id, pubitername, image_contents.read())
        print(results)
    return results
