from Parley.Utils.ExtractionUtils import *
from Parley.Utils.PDFUtils import *
from pdf2image import convert_from_path
from PIL import ImageDraw, Image

class DebugUtils:

    def debug_pdf_annotations(pdf_file_path):
        bar_lines = PDFUtils.get_bar_lines(pdf_file_path)
        print(len(bar_lines))
        images = convert_from_path(pdf_file_path)
        contexts = [ImageDraw.Draw(i) for i in images]
        for bar_line in bar_lines:
            bar_line = bar_line.scale_to_image(images[bar_line.page_num])
            context = contexts[bar_line.page_num]
            context.line(((bar_line.x1, bar_line.y1), (bar_line.x2, bar_line.y2)), width=10, fill="red")
        for ind, image in enumerate(images):
            image.save(f"./Temp/page_{ind}.jpg")


    def debug_durations(composition):
        for track_num in ExtractionUtils.get_track_nums(composition):
            print("=================", "track_num:", track_num, "=================")
            for episode in composition.form.episodes:
                for bar in episode.bars:
                    print("=== bar", bar.comp_bar_num, "duration", bar.duration_ticks, "===")
                    for note_sequence in bar.note_sequences:
                        if note_sequence.track_num == track_num:
                            note_duration_ticks = 0
                            for note in note_sequence.notes:
                                note_duration_ticks += note.duration_ticks
                                print(track_num, note.pitch, note.duration_ticks, note_duration_ticks)



    def check_tied_durations(composition, track_num):
        track_notes_hash = ExtractionUtils.get_track_notes_for_composition(composition)
        notes = track_notes_hash[track_num]
        for ind, note in enumerate(notes):
            if note.tie_type is None or note.tie_type == "start":
                dts = note.tied_duration_ticks if note.tied_duration_ticks is not None else note.duration_ticks
                flag = "" if note.tied_duration_ticks is None else "*"
                print(ind, note.duration_ticks, dts, flag)
            else:
                print(ind, note.duration_ticks, "0")
                print("---")

    def check_composition_durations(composition):
        track_notes_hash = ExtractionUtils.get_track_notes_for_composition(composition)
        for track_num in ExtractionUtils.get_track_nums(composition):
            notes = track_notes_hash[track_num]
            num_ticks = 0
            for note in notes:
                if note.tie_type is None or note.tie_type == "start":
                    dts = note.tied_duration_ticks if note.tied_duration_ticks is not None else note.duration_ticks
                    num_ticks += dts
            print(track_num, num_ticks)

    def check_bar_durations(composition, track_num_to_debug=None):
        for track_num in ExtractionUtils.get_track_nums(composition):
            if track_num_to_debug is None or track_num_to_debug == track_num:
                print("=================")
                print("TRACK", track_num)
                bar_num = 0
                total_note_ticks = 0
                total_bar_ticks = 0
                for episode in composition.form.episodes:
                    for bar in episode.bars:
                        bar_num += 1
                        for note_sequence in bar.note_sequences:
                            if note_sequence.track_num == track_num:
                                ts = ""
                                total_note_ticks_in_bar = 0
                                for note in note_sequence.notes:
                                    if note.tie_type is None or note.tie_type == "start":
                                        dts = note.tied_duration_ticks if note.tied_duration_ticks is not None else note.duration_ticks
                                        total_note_ticks += dts
                                        addon = "(s)" if note.tie_type == "start" else ""
                                        ts += f"{dts}{addon} "
                                    else:
                                        addon = "(e)" if note.tie_type == "end" else ""
                                        addon = "(m)" if note.tie_type == "mid" else addon
                                        ts += f"->{note.duration_ticks}{addon} "
                                total_bar_ticks += bar.duration_ticks
                                equal = "---" if abs(total_note_ticks - total_bar_ticks) < 5 else ""
                                num_notes = len(note_sequence.notes)
                                if bar_num < 5:
                                    print(bar_num, total_note_ticks, total_bar_ticks, num_notes, equal, "    ", ts)

