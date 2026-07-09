from manim import *
import random

'''
Function to generate mental rotation tests
Usage: manim -pql -r 1080,1080 gen_grid.py QuestionScene_1
Storage: media/images/gen_grid/
'''

# Function for transformation of matrix
def rotate_matrix(matrix):
    if not matrix: return matrix
    n = len(matrix)
    new_matrix = [[None] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            new_matrix[n - 1 - c][r] = matrix[r][c]
    return new_matrix


def flip_matrix_horizontal(matrix):
    return [row[::-1] for row in matrix]


def flip_matrix_vertical(matrix):
    return matrix[::-1]


def flip_matrix_diagonal(matrix):
    if not matrix: return matrix
    n = len(matrix)
    new_matrix = [[None] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            new_matrix[c][r] = matrix[r][c]
    return new_matrix


# Color legend
COLOR_LEGEND = {
    "_": None,
    "R": RED,
    "B": BLUE,
    "G": GREEN,
    "Y": YELLOW,
    "O": ORANGE,
    "P": PURPLE,
    "C": TEAL,
    "M": WHITE,
    "L": PINK,
    "S": "#8F00FF",  # VIOLET
}


# Helper function to map a line into a symbol matrix
def parse_grid_string(grid_str):
    lines = grid_str.strip().split('\n')
    char_matrix = [line.strip().split() for line in lines]
    char_matrix.reverse()
    return char_matrix


# Function to apply by name
def apply_transformation(matrix, transform_name):
    current_matrix = [row[:] for row in matrix]

    if transform_name == "none":
        return current_matrix
    elif transform_name == "90":
        return rotate_matrix(current_matrix)
    elif transform_name == "180":
        return rotate_matrix(rotate_matrix(current_matrix))
    elif transform_name == "270":
        return rotate_matrix(rotate_matrix(rotate_matrix(current_matrix)))
    elif transform_name == "hori":
        return flip_matrix_horizontal(current_matrix)
    elif transform_name == "vert":
        return flip_matrix_vertical(current_matrix)
    elif transform_name == "diag":
        return flip_matrix_diagonal(current_matrix)
    elif transform_name == "90_hori":
        return flip_matrix_horizontal(rotate_matrix(current_matrix))
    elif transform_name == "90_vert":
        return flip_matrix_vertical(rotate_matrix(current_matrix))
    elif transform_name == "180_hori":
        return flip_matrix_horizontal(rotate_matrix(rotate_matrix(current_matrix)))
    elif transform_name == "hori_90":
        return rotate_matrix(flip_matrix_horizontal(current_matrix))
    elif transform_name == "90_diag":
        return flip_matrix_diagonal(rotate_matrix(current_matrix))
    elif transform_name == "180_diag":
        return flip_matrix_diagonal(rotate_matrix(rotate_matrix(current_matrix)))
    else:
        raise ValueError(f"Unknown transformation: {transform_name}")


# Class to display 1 grid
class GridMobject(VGroup):
    def __init__(self, char_matrix, cell_size, **kwargs):
        super().__init__(**kwargs)
        n = len(char_matrix)
        if n == 0: return

        grid_group = VGroup()
        for r in range(n):
            for c in range(n):
                square = Square(side_length=cell_size, stroke_color=WHITE).move_to(
                    [(c - n / 2 + 0.5) * cell_size, (r - n / 2 + 0.5) * cell_size, 0]
                )
                grid_group.add(square)

        for row_idx, row in enumerate(char_matrix):
            for col_idx, char_code in enumerate(row):
                color = COLOR_LEGEND.get(char_code)
                if color:
                    flat_index = row_idx * n + col_idx
                    if 0 <= flat_index < len(grid_group):
                        grid_group[flat_index].set_fill(color, opacity=1)

        self.add(*grid_group)
        bbox = SurroundingRectangle(self, buff=0.05, color=WHITE, stroke_width=2)
        self.add(bbox)


# Class to display 1 question
class MentalRotationQuestion(Scene):
    def construct(self):
        pass

    def render_question(self, question_data):
        test_grid_str = question_data["test_grid"]
        correct_transform = question_data["correct_transform"]
        distractor_transforms = question_data["distractor_transforms"]
        question_number = question_data["number"]
        difficulty_level = question_data["difficulty"]
        cell_size = question_data.get("cell_size", 0.9)

        base_matrix = parse_grid_string(test_grid_str)
        n = len(base_matrix)
        if n == 0: return

        transformed_correct = apply_transformation(base_matrix, correct_transform)

        final_distractors_matrices = []
        for t_name in distractor_transforms:
            if t_name.startswith("modified_"):
                mod_matrix = apply_transformation(base_matrix, t_name.replace("modified_", ""))
                mod_matrix_copy = [row[:] for row in mod_matrix]
                valid_cells = [(r, c) for r in range(n) for c in range(n) if mod_matrix_copy[r][c] != '_']
                if valid_cells:
                    r_idx, c_idx = random.choice(valid_cells)
                    original_char = mod_matrix_copy[r_idx][c_idx]
                    available_colors_chars = [c for c in COLOR_LEGEND.keys() if c != '_']
                    possible_new_chars = [c for c in available_colors_chars if c != original_char] + ['_']
                    new_char = random.choice(possible_new_chars)
                    mod_matrix_copy[r_idx][c_idx] = new_char
                final_distractors_matrices.append(mod_matrix_copy)
            else:
                final_distractors_matrices.append(apply_transformation(base_matrix, t_name))

        test_mobject_grid = GridMobject(base_matrix, cell_size=cell_size)

        options_data = [transformed_correct] + final_distractors_matrices
        random.shuffle(options_data)

        options_mobjects = VGroup(*[GridMobject(opt_matrix, cell_size=cell_size) for opt_matrix in options_data])

        # Determine correct question
        correct_index = options_data.index(transformed_correct)
        correct_answer = chr(65 + correct_index)  # A, B, C

        test_mobject_grid.move_to(LEFT * 4.5)
        options_mobjects.arrange(DOWN, buff=0.7).next_to(test_mobject_grid, RIGHT, buff=2)

        question_text = Text(f"", font_size=36,
                             color=WHITE).to_edge(UP + LEFT)
        test_label = Text("", font_size=28, color=WHITE).next_to(test_mobject_grid, UP)
        options_labels = VGroup(
            *[Text(chr(65 + i), font_size=28, color=WHITE).next_to(option_mobj, LEFT, buff=0.5) for i, option_mobj in
              enumerate(options_mobjects)])
        options_area_label = Text("", font_size=28, color=WHITE).next_to(options_mobjects.get_top(), UP)

        # Add correct answer
        answer_text = Text(f"", font_size=20, color=GRAY).to_corner(DOWN + RIGHT)

        # Resize
        all_content = VGroup(question_text, test_label, test_mobject_grid, options_area_label,
                             options_labels, options_mobjects, answer_text)
        if all_content.width > 13 or all_content.height > 13:
            scale_factor = min(13 / all_content.width, 13 / all_content.height)
            all_content.scale(scale_factor)

        all_content.move_to(ORIGIN)

        self.add(all_content)


# Data for 20 levels
LEVELS_DATA = [
    {"number": 1, "difficulty": 1, "cell_size": 1.2, "test_grid": "_ Y _\nP R _\n_ G _", "correct_transform": "90",
     "distractor_transforms": ["270", "180"]},
    {"number": 2, "difficulty": 2, "cell_size": 1.2, "test_grid": "R B Y\n_ P _\nG O _", "correct_transform": "180",
     "distractor_transforms": ["hori", "90"]},
    {"number": 3, "difficulty": 3, "cell_size": 1.0, "test_grid": "_ Y _ R\nP _ B _\n_ G _ Y\nO _ P _",
     "correct_transform": "270", "distractor_transforms": ["90", "180"]},
    {"number": 4, "difficulty": 4, "cell_size": 1.0, "test_grid": "R B _ Y\nP _ G _\nC _ O R\n_ B P _",
     "correct_transform": "90", "distractor_transforms": ["vert", "hori"]},
    {"number": 5, "difficulty": 5, "cell_size": 0.8,
     "test_grid": "R _ B _ Y\n_ P G _ _\nC _ _ O R\n_ _ B P _\nY G _ _ C", "correct_transform": "90",
     "distractor_transforms": ["hori", "modified_90"]},
    {"number": 6, "difficulty": 6, "cell_size": 0.8,
     "test_grid": "R B G Y P\n_ C _ M _\nL O _ _ _\n_ _ _ B _\nP Y G _ R", "correct_transform": "180",
     "distractor_transforms": ["hori", "modified_180"]},
    {"number": 7, "difficulty": 7, "cell_size": 0.7,
     "test_grid": "R _ B G _ Y\nP C _ M _ O\n_ _ L _ _ _\nG _ _ Y P _\nB _ R _ C _\n_ O _ P _ M",
     "correct_transform": "180", "distractor_transforms": ["hori", "vert"]},
    {"number": 8, "difficulty": 8, "cell_size": 0.7,
     "test_grid": "R B G Y P C\nM O L _ _ _\n_ _ _ R B _\nG Y P C M O\nL _ _ _ _ R\n_ B _ G _ Y",
     "correct_transform": "90", "distractor_transforms": ["hori_90", "hori"]},
    {"number": 9, "difficulty": 9, "cell_size": 0.6,
     "test_grid": "R _ B _ G _ Y\nP C _ M _ O _\n_ L _ R _ B _\nG _ Y P _ C _\n_ M _ O _ L _\nR _ B _ G _ Y\n_ P C _ M _ O",
     "correct_transform": "270", "distractor_transforms": ["90_diag", "180_diag"]},
    {"number": 10, "difficulty": 10, "cell_size": 0.6,
     "test_grid": "R _ G Y _ C _\nO _ _ B G _ P\nC _ O L R _ G\nY P _ _ O _ _\nB _ Y _ _ _ O\nL R B _ Y P C\n_ O L R B _ Y",
     "correct_transform": "180", "distractor_transforms": ["180_hori", "hori"]},
    {"number": 11, "difficulty": 11, "cell_size": 0.6,
     "test_grid": "R B _ G Y _ P\nC _ M O _ L _\n_ R _ B G _ Y\nP _ C _ M O _\nL _ _ R _ B G\n_ Y P _ C _ M\nO _ L _ _ R _",
     "correct_transform": "90", "distractor_transforms": ["90_diag", "diag"]},
    {"number": 12, "difficulty": 12, "cell_size": 0.6,
     "test_grid": "R _ B _ G _ Y\n_ P C _ M _ O\nL _ _ R B _ _\n_ G Y _ P C _\nM _ _ O L _ R\n_ B _ G _ Y P\nC _ M _ O _ L",
     "correct_transform": "180", "distractor_transforms": ["hori", "modified_90"]},
    {"number": 13, "difficulty": 13, "cell_size": 0.55,
     "test_grid": "R B G _ Y P _ C\n_ M O L _ _ R B\nG _ Y _ P C M _\n_ O L R _ _ B G\nY _ P C _ M O _\nL R _ _ B G Y P\n_ C M O _ L _ R\nB _ G Y P _ C M",
     "correct_transform": "270", "distractor_transforms": ["diag", "modified_270"]},
    {"number": 14, "difficulty": 14, "cell_size": 0.55,
     "test_grid": "R _ B G _ Y P _\nC M _ O L _ _ R\n_ B G Y _ P C M\nO _ L R B _ G _\n_ Y P _ C M _ O\nL _ R B _ G Y _\nP C _ M O _ L R\n_ G Y _ P C _ B",
     "correct_transform": "90", "distractor_transforms": ["90_vert", "vert"]},
    {"number": 15, "difficulty": 15, "cell_size": 0.55,
     "test_grid": "R _ B G _ Y P _\nC M _ O L R _ _\n_ B G Y _ P C M\nO _ L R B _ G Y\n_ Y P _ C M _ O\nL _ R B _ G Y P\nP C _ M O _ L R\n_ G Y _ P C M B",
     "correct_transform": "180", "distractor_transforms": ["180_diag", "diag"]},
    {"number": 16, "difficulty": 16, "cell_size": 0.5,
     "test_grid": "R B _ G Y _ P C _\n_ M O _ L R _ _ B\nG _ Y P _ C M O _\nL _ R _ B G _ Y P\n_ C M O _ _ L R B\nG Y _ P C _ M _ O\n_ L R B _ G Y P _\nC _ M _ O L _ R B\nG _ Y P _ C M _ _",
     "correct_transform": "180", "distractor_transforms": ["180_hori", "modified_hori"]},
    {"number": 17, "difficulty": 17, "cell_size": 0.5,
     "test_grid": "R _ B G Y _ P C M\nO _ L _ R B _ G _\n_ Y P C _ M O L _\nR _ B _ G Y _ P C\n_ M O L _ R B _ G\nY _ P _ C M _ O L\n_ R B G _ Y P _ C\nM _ O _ L R _ B G\n_ Y P C _ M O _ L",
     "correct_transform": "270", "distractor_transforms": ["90_diag", "modified_diag"]},
    {"number": 18, "difficulty": 18, "cell_size": 0.45,
     "test_grid": "R B G _ Y P C _ M O\n_ L _ R B _ G Y _ P\nC M _ O L _ R _ B G\nY _ P C _ M O L _ R\n_ B G Y _ P _ C M _\nO L _ R B _ G _ Y P\n_ C M O _ L R B _ G\nY P _ C M _ O _ L R\nB _ G Y P _ C M _ O\n_ L R _ B G _ Y P C",
     "correct_transform": "90", "distractor_transforms": ["90_diag", "modified_diag"]},
    {"number": 19, "difficulty": 19, "cell_size": 0.45,
     "test_grid": "R B G _ Y P C _ M O\n_ L R _ B _ G Y _ P\nC M _ O L _ R _ B G\nY _ P C _ M O L _ R\n_ B G Y _ P _ C M _\nO L _ R B _ G _ Y P\nP C M O _ L R B _ G\nY P _ C M _ O _ L R\nB _ G Y P _ C M R O\n_ L R _ B G _ Y P C",
     "correct_transform": "180", "distractor_transforms": ["180_diag", "modified_180_diag"]},
    {"number": 20, "difficulty": 20, "cell_size": 0.45,
     "test_grid": "R _ B G _ Y P _ C M\nO L _ R _ B G Y _ P\nC _ M _ O L R _ B G\nG Y _ P C _ M O _ L\nR B _ G Y _ P C M O\n_ O L _ R B _ G _ Y\nP C _ M O _ L R _ B\nL G Y P _ C M _ O L\nR _ B _ G Y _ P C M\nM O _ L R _ B G _ Y",
     "correct_transform": "90", "distractor_transforms": ["modified_180_hori", "modified_90"]},
]

# Scene
for i, q_data in enumerate(LEVELS_DATA):
    scene_class_name = f"QuestionScene_{i + 1}"
    def make_construct(question_data):
        def construct(self):
            self.render_question(question_data)

        return construct

    globals()[scene_class_name] = type(
        scene_class_name,
        (MentalRotationQuestion,),
        {"construct": make_construct(q_data)}
    )
