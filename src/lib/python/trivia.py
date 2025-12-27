from random import randint
from sys import argv
from json import loads

import moviepy.editor as editor
from moviepy.video.fx.resize import resize
from moviepy.audio.fx.volumex import volumex
from lib.python.text_generator import create_text_clip



clip_durations = {
    "question": 10,
    "answer": 2.5
}
full_question_duration = sum(clip_durations.values())


class Question:
    title: str
    answers: list[str]
    correct_answer: int

    def __init__(self):
        self.answers = []


def produce_short(
    questions: list[Question],
    background: str,
    music: str,
    font: str,
    output: str,
    logger=None
):
    question_count = len(questions)

    background_duration = editor.VideoFileClip(background).duration
    background = resize(
        (
            editor.VideoFileClip(background)
            .cutout(0, randint(1, round(background_duration) - 65))
            .set_duration(full_question_duration * question_count)
            .set_position(("center", "center"))
        ),
        height=1920
    )

    dimmer = (
        editor.ColorClip(size=(1080, 1920), color=(0,0,0))
        .set_opacity(0.4)
        .set_duration(full_question_duration * question_count)
    )

    music_duration = editor.AudioFileClip(music).duration
    music = volumex(
        editor.CompositeAudioClip([
            editor.AudioFileClip(music)
            .cutout(0, randint(
                1, 
                int(music_duration - full_question_duration * question_count)
            ))
            .set_end(full_question_duration * question_count)
        ]),
        0.6
    )

    clips = []

    for question_index, question in enumerate(questions):
        question_text = (
            create_text_clip(
                question["title"],
                fontsize=90, 
                color="white", 
                stroke_color="black", 
                stroke_width=4,
                method="caption",
                size=(1080, None),
                font_path=font
            )
            .set_position(("center", 0.15), relative=True)
            .set_start(question_index * full_question_duration)
            .set_duration(clip_durations["question"])
        )
        clips.append(question_text)

        answer_texts = [
            (
                create_text_clip(
                    f"{list('ABCD')[i]} - {question['answers'][i]}", 
                    fontsize=90, 
                    color="white", 
                    stroke_color="black", 
                    stroke_width=4,
                    method="caption",
                    size=(1080, None),
                    font_path=font
                )
                .set_position(("center", 0.4 + (i / 7)), relative=True)
                .set_start(question_index * full_question_duration)
                .set_duration(clip_durations["question"])
            ) for i in range(len(question["answers"]))
        ]
        clips += answer_texts

        countdown_texts = [
            (
                create_text_clip(
                    str(clip_durations["question"] - i), 
                    fontsize=120, 
                    color="white", 
                    stroke_color="black", 
                    stroke_width=4,
                    method="caption",
                    size=(1080, None),
                    font_path=font
                )
                .set_start(question_index * full_question_duration + i)
                .set_duration(1)
                .set_position(("center", 0.9), relative=True)
            ) for i in range(clip_durations["question"])
        ]
        clips += countdown_texts

        correct_answer_text = (
            create_text_clip(
                question["answers"][question["correct"]], 
                fontsize=120, 
                color="#4ADE80", 
                stroke_color="black", 
                stroke_width=4,
                method="caption",
                size=(1080, None),
                font_path=font
            )
            .set_start(question_index * full_question_duration + clip_durations["question"])
            .set_duration(clip_durations["answer"])
            .set_position("center")
        )
        clips.append(correct_answer_text)

    result: editor.CompositeVideoClip = (
        editor.CompositeVideoClip(
            [
                background,
                dimmer,
                *clips
            ], 
            size=(1080, 1920)
        )
        .set_audio(music)
    )

    result.write_videofile(
        output, 
        fps=24, 
        audio_codec="aac",
        threads=4,
        temp_audiofile="out/TEMP_trivia.mp4",
        logger=logger
    )

    result.close()
    music.close()
    background.close()

if __name__ == "__main__":
    args = loads(argv[1])
    
    produce_short(
        questions=args["questions"],

        background=args["assets"]["background"],
        music=args["assets"]["music"],
        font=args["assets"]["font"],

        output=args["output"]
    )