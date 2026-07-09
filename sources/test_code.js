const jsPsych = initJsPsych({
  on_finish: function() {}
});

var timeline = [];

var show_instructions_flag = false;
var practice_attempt_index = 0;

// WELCOME
var welcome_screen = {
  type: jsPsychHtmlButtonResponse,
  stimulus: `
  <div style="position: fixed; top: 20px; right: 20px; color: #333; font-size: 16px;text-align:right">
        Czech Technical University in Prague<br>Faculty of Electrical Engineering<br>Kamoliddin Bakhriddinov<br>Danil Zyryanov<br>Kirill Ussov
    </div>
  <h1>Welcome</h1>
  <p>Thank you for participating in this mental rotation research.</p>
  <p>
  Our goal is to investigate mental rotation abilities among university students<br>
  and compare them to latest LLMs ones.
  </p>
  <p>Please maximize your browser window.</p>
  <br>
  `,
  choices: ['Let\'s Begin']
};
timeline.push(welcome_screen);

// DEMOGRAPHICS
var demographics = {
  type: jsPsychSurveyHtmlForm,
  preamble: '<h2>Please tell us about yourself</h2>',
  html: `
  <div style="text-align: left; max-width: 500px; margin: 0 auto;">
  <label>Sex (optional):</label> <input type="radio" name="sex" value="Male"> Male <input type="radio" name="sex" value="Female"> Female<br><br>
  <label>Age:</label> <input type="number" name="age" required><br><br>
  <label>How many hours did you sleep last night? (hrs):</label> <input type="number" name="sleep" step="0.5" required><br><br>
  <label>How well rested are you? (1-10):</label> <input type="number" name="energy" min="1" max="10" required>
  </div>
  <br>
  `,
  button_label: 'Next',
  data: {
    task: 'demographics_form'
  }
};
timeline.push(demographics);

// INSTRUCTIONS
var instructions_content = {
  type: jsPsychHtmlButtonResponse,
  stimulus: `
  <h2>Instructions</h2>
  <img src="https://cdn.cognition.run/resources/xaobvfzwnw/RotationAroundCommonCenter_ManimCE_v0.19.0.gif?id=1764023208" style="max-width:400px;">
  <div style="text-align:left; max-width:600px; margin:auto;">
  <p>
  The test consists of several tasks. In each task you will be shown a scene consisting of 2D objects.
  </p>
  <p>
  Only <strong>ONE</strong> option (A, B, or C) is correct. Your goal is
  to find an option, which can be obtained by applying rotation to the original scene.
  </p>
  <p>
  Rotation principle: all objects are rotated around the <strong>THE CENTER OF ALL OBJECTS</strong>.
  <br>You have to answer the question that will be displayed.
  </p>
  </div>
  `,
  choices: ['I understand']
};
timeline.push(instructions_content);

// PRACTICE SECTION

var practice_list = [{
  q: "https://cdn.cognition.run/resources/xaobvfzwnw/4571ff1e-a0b7-4c86-989d-9b0985c3f81a.jpeg?id=1764017765",
  correct: 1,
  prompt: "Which of these images (A, B, C) is a 90° clockwise rotation of the TEST image?"
},
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/8705f29f-b19c-4edf-8423-2b6090d68e90.jpeg?id=1764018677",
    correct: 0,
    prompt: "Which of these images (A, B, C) is a 180° clockwise rotation of the TEST image?"
  }];

var conditional_instructions = {
  timeline: [instructions_content],
  conditional_function: function() {
    return show_instructions_flag;
  }
};

var practice_trial = {
  type: jsPsychHtmlButtonResponse,
  stimulus: function() {
    var current_q = practice_list[practice_attempt_index];
    return `
    <div style="margin-bottom: 20px;">
    <h3>Practice Question ${practice_attempt_index + 1}</h3>
    <p style="font-size: 22px; font-weight: bold; color: #333; margin: 20px 0;">
    ${current_q.prompt}
    </p>
    <img src="${current_q.q}" style="max-width:500px; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
    </div>
    <p>Select the correct option:</p>
    `;
  },
  choices: ['A',
    'B',
    'C'],
  button_html: '<button class="jspsych-btn" style="font-size: 20px; padding: 10px 40px; margin: 0 15px; width: 100px;">%choice%</button>',
  data: {
    task: 'practice_response'
  },
  on_finish: function(data) {
    var current_q = practice_list[practice_attempt_index];
    data.correct = (data.response == current_q.correct);
  }
};

var practice_feedback = {
  type: jsPsychHtmlButtonResponse,
  stimulus: function() {
    var last_trial = jsPsych.data.get().filter({
      task: 'practice_response'
    }).last(1).values()[0];

    if (last_trial.correct) {
      return `<h2 style="color:green; margin-top: 50px;">Correct!</h2>
      <p>You clearly understand the rules.</p>`;
    } else {
      var html = `<h2 style="color:red; margin-top: 50px;">Incorrect</h2>
      <p>That was not the correct choice.</p>`;

      if (practice_attempt_index === 0) {
        html += `<p>Solution for Practice 1:</p>
        <img src="https://cdn.cognition.run/resources/xaobvfzwnw/trial_1.png?id=1764710190" style="max-width:300px;">`;
      } else {
        html += `<p>Solution for Practice 2:</p>
        <img src="https://cdn.cognition.run/resources/xaobvfzwnw/trial_2.png?id=1764710190" style="max-width:300px;">`;
      }
      return html;
    }
  },
  choices: function() {
    var last_trial = jsPsych.data.get().filter({
      task: 'practice_response'
    }).last(1).values()[0];

    if (last_trial.correct) {
      return ['Start Real Test'];
    } else {
      if (practice_attempt_index === 0) {
        return ['Read Instructions',
          'Try One More Time'];
      } else {
        return ['Read Instructions One More Time'];
      }
    }
  },
  on_finish: function(data) {
    var last_trial = jsPsych.data.get().filter({
      task: 'practice_response'
    }).last(1).values()[0];
    show_instructions_flag = false;

    if (!last_trial.correct) {
      var choice_label = jsPsych.data.get().last(1).values()[0].response;
      if (practice_attempt_index === 0) {
        if (choice_label == 0) {
          show_instructions_flag = true;
          practice_attempt_index = 0;
        } else {
          practice_attempt_index = 1;
        }
      } else {
        show_instructions_flag = true;
        practice_attempt_index = 0;
      }
    }
  }
};

var practice_loop = {
  timeline: [conditional_instructions,
    practice_trial,
    practice_feedback],
  loop_function: function(data) {
    var last_trial = data.filter({
      task: 'practice_response'
    }).last(1).values()[0];
    return !last_trial.correct;
  }
};
timeline.push(practice_loop);


// REAL EXPERIMENT

var real_stimuli = [{
  q: "https://cdn.cognition.run/resources/xaobvfzwnw/1.jpeg?id=1764021511",
  correct: 1,
  // b
  prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
},
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/2.jpeg?id=1764021511",
    correct: 2,
    // c
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/3.png?id=1764024253",
    correct: 0,
    // a
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/4.png?id=1764021511",
    correct: 2,
    // c
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/5.png?id=1764021511",
    correct: 0,
    // a
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/6.png?id=1764021511",
    correct: 2,
    // c
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/7.jpeg?id=1764021511",
    correct: 2,
    // c
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/8.png?id=1764025790",
    correct: 0,
    // a
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/9.png?id=1764025790",
    correct: 2,
    //c
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  },
  {
    q: "https://cdn.cognition.run/resources/xaobvfzwnw/10.jpeg?id=1764021511",
    correct: 1,
    //b
    prompt: "Which of these images (A, B, C) is a rotation of the TEST image?"
  }];

var real_trial = {
  type: jsPsychHtmlButtonResponse,
  stimulus: function() {
    var current_prompt = jsPsych.timelineVariable('prompt');
    var current_img = jsPsych.timelineVariable('q');

    return `
    <div style="margin-bottom: 30px;">
    <p style="font-size: 24px; font-weight: bold; margin-bottom: 25px; color: #000;">
    ${current_prompt}
    </p>
    <img src="${current_img}" style="max-width:600px; border: 1px solid #ddd; padding: 5px;">
    </div>
    `;
  },
  choices: ['A',
    'B',
    'C'],
  button_html: '<button class="jspsych-btn" style="font-size: 20px; padding: 10px 40px; margin: 0 15px; width: 100px;">%choice%</button>',
  data: {
    task: 'response'
  },
  on_finish: function(data) {
    var correct_index = jsPsych.timelineVariable('correct');
    data.correct = (data.response == correct_index);
  }
};

var fixation = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: '<div style="font-size:60px;">+</div>',
  choices: "NO_KEYS",
  trial_duration: 500
};

var experiment_procedure = {
  timeline: [fixation,
    real_trial],
  timeline_variables: real_stimuli,
  randomize_order: false
};
timeline.push(experiment_procedure);


// STRATEGY SURVEY
var strategy_survey = {
  type: jsPsychSurveyHtmlForm,
  preamble: '<h2>Strategy Questionnaire</h2>',
  html: `
  <div style="text-align: left; max-width: 600px; margin: 0 auto;">
  <label for="strategy_text" style="font-size: 18px; font-weight: bold;">
  How did you solve these tasks? Please describe the strategy or tactics you applied:
  </label>
  <br><br>
  <textarea id="strategy_text" name="strategy" rows="6" style="width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px;" required></textarea>
  </div>
  <br>
  `,
  button_label: 'See Results',
  data: {
    task: 'strategy_form'
  }
};
timeline.push(strategy_survey);


// FINISH & DATA SAVING

var debrief = {
  type: jsPsychHtmlButtonResponse,
  choices: ['Finish and Save Data'],
  stimulus: function() {
    var trials = jsPsych.data.get().filter({
      task: 'response'
    });
    var correct = trials.filter({
      correct: true
    });
    var accuracy = trials.count() > 0 ? Math.round(correct.count() / trials.count() * 100): 0;
    var rt = (correct.count() > 0) ? Math.round(correct.select('rt').mean()): 0;

    return `
    <div style="margin-top: 5%;">
    <h1 style="color:green;">Complete!</h1>
    <p>Thank you for participating.</p>
    <hr style="width:50%; margin: 20px auto;">
    <p style="font-size: 1.2em;"><strong>Accuracy:</strong> ${accuracy}%</p>
    <p style="font-size: 1.2em;"><strong>Avg Reaction Time:</strong> ${rt}ms</p>
    <br>
    <p>Click the button below to save your data and exit.</p>
    </div>
    `;
  },
  on_load: function() {
    var demo_trial = jsPsych.data.get().filter({
      task: 'demographics_form'
    }).last(1).values()[0];
    var demo_data = demo_trial ? demo_trial.response: {};

    var strat_trial = jsPsych.data.get().filter({
      task: 'strategy_form'
    }).last(1).values()[0];
    var strat_data = strat_trial ? strat_trial.response: {};

    jsPsych.data.addProperties({
      Participant_Sex: demo_data.sex || "NA",
      Participant_Age: demo_data.age || "NA",
      Participant_Sleep: demo_data.sleep || "NA",
      Participant_Energy: demo_data.energy || "NA",
      Participant_Strategy: strat_data.strategy || "NA"
    });

    console.log("Data ready for save.");
  }
};
timeline.push(debrief);

jsPsych.run(timeline);