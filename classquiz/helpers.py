from classquiz.db.models import Quiz, User
import xlsxwriter
from aiohttp import ClientSession
from io import BytesIO
from PIL import Image


async def get_meili_data(quiz: Quiz) -> dict:
    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description,
        "user": (await User.objects.filter(id=quiz.user_id).first()).username,
        "created_at": int(quiz.created_at.timestamp()),
    }


async def generate_spreadsheet(quiz_results: dict, quiz: Quiz, with_images: bool = True) -> BytesIO:
    storage = BytesIO()
    workbook = xlsxwriter.Workbook(storage, {"in_memory": True})
    worksheet = workbook.add_worksheet()
    worksheet.name = "Questions"
    worksheet.write(0, 0, "Question")
    worksheet.write(0, 1, "Time")
    worksheet.write(0, 2, "Image")
    worksheet.write(0, 3, "Correct answers")
    worksheet.write(0, 4, "Correct answers")
    worksheet.write(0, 5, "Wrong answers")
    for i, _ in enumerate(quiz_results):
        question = quiz.questions[i]
        answer_data = quiz_results[str(i)]
        worksheet.write(i + 1, 0, question["question"])
        worksheet.write(i + 1, 1, question["time"])
        if with_images and question["image"] != "" or question["image"] is not None:
            async with ClientSession() as session, session.get(question["image"]) as response:
                img_data = BytesIO(await response.read())
                worksheet.insert_image(i + 1, 2, question["image"], {"image_data": img_data})
                image = Image.open(img_data)
                worksheet.set_row(i + 1, image.height)
                worksheet.set_column(2, 2, image.width)
        answer_amount = len(answer_data)
        correct_answers = 0
        wrong_answers = 0
        for j in answer_data:
            j_correct = j["right"]
            if j_correct:
                correct_answers += 1
            else:
                wrong_answers += 1
        worksheet.write(i + 1, 3, f"{round(correct_answers / answer_amount * 100)}%")
        worksheet.write(i + 1, 4, correct_answers)
        worksheet.write(i + 1, 5, wrong_answers)

        ws = workbook.add_worksheet(f"{i + 1}. Question")
        ws.write(0, 0, "Answer")
        ws.write(0, 1, "Correct")
        ws.write(0, 2, "Username")
        for j in range(len(answer_data)):
            ws.write(j + 1, 0, answer_data[j]["answer"])
            if answer_data[j]["right"]:
                ws.write(j + 1, 1, "True")
            else:
                ws.write(j + 1, 1, "False")
            ws.write(j + 1, 2, answer_data[j]["username"])

    workbook.close()
    storage.seek(0)
    return storage
