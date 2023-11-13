extensions [csv table py time]

; Define a breed of agents called "students"
breed [students student]

; Global variables to keep track of the current time, number of students, data, counter, and weeks
globals [
  current-time  ; Variable to keep track of the current time (in hours)
  data ;
]

; Patches own variables to represent the floor number and max-occupancy of the patch
patches-own [
  floor-number  ; The floor number of the patch
  max-occupancy ; max-occupancy for that floor
]

; Students own variables representing their initial behavior, preferred floor, time, and current behavior
students-own [
  initial-behavior  ; Behavior of the student (e.g., studying, chope)
  preferred-floor  ; Preferred floor to study
  time             ; Time attribute for student
  current-behavior ; Current behavior of the student
]

; Initial setup procedure
to setup
  clear-all
  ; Setup Python extension and import necessary libraries
  py:setup py:python
  py:run "import pandas as pd"
  py:run "import numpy"
  py:run "import math"

  ; Set week, day, and initialize data
  py:set "week" week
  py:set "day" day
  setup-data
  setup-time-hour
  setup-floors

  ; Set default shape for students to "person"
  set-default-shape students "person"

  ; Initialize ticks
  reset-ticks
end

; Procedure to set up data, reading from a CSV file
to setup-data
  py:run "data =pd.read_csv('datasets/clean_df.csv',index_col=False)"
  py:run "data['Datetime'] = pd.to_datetime(data['Datetime'])"
  py:run "data['Date'] = pd.to_datetime(data['Date'])"
  py:run "data = data.sort_values(by = ['Datetime'])"
  py:run "data['Time'] = data['Datetime'].dt.time"
  py:run "level_survey = pd.read_csv('datasets/floor.csv')"
end

; Procedure to set up time based on the week
to setup-time-hour
  ; Depending on the week, set the data for the current day
  if week = "Normal" [
    set data py:runresult "(data[(data['Datetime'].dt.month == 1) & (data['Datetime'].dt.dayofweek == 2)]).astype(str).values.tolist() if data[(data['Datetime'].dt.month == 1) & (data['Datetime'].dt.dayofweek == day - 1)].empty else (data[(data['Datetime'].dt.month == 1) & (data['Datetime'].dt.dayofweek == day - 1)]).astype(str).values.tolist()"
  ]
  if week = "Recess" [
    set data py:runresult "(data[(data['Datetime'].dt.month == 2) & (data['Datetime'].dt.dayofweek == 2)]).astype(str).values.tolist() if data[(data['Datetime'].dt.month == 2) & (data['Datetime'].dt.dayofweek == day - 1)].empty else (data[(data['Datetime'].dt.month == 2) & (data['Datetime'].dt.dayofweek == day - 1)]).astype(str).values.tolist()"
  ]
  if week = "Reading" [
    set data py:runresult "(data[(data['Datetime'].dt.month == 4) & (data['Datetime'].dt.dayofweek == 2) & (data['Datetime'].dt.day <= 21)]).astype(str).values.tolist() if data[(data['Datetime'].dt.month == 4) & (data['Datetime'].dt.dayofweek == day - 1) & (data['Datetime'].dt.day <= 21)].empty else (data[(data['Datetime'].dt.month == 4) & (data['Datetime'].dt.dayofweek == day - 1) & (data['Datetime'].dt.day <= 21)]).astype(str).values.tolist()"
  ]
  if week = "Exam" [
    set data py:runresult "(data[(data['Datetime'].dt.month == 4) & (data['Datetime'].dt.dayofweek == 2) & (data['Datetime'].dt.day > 21)]).astype(str).values.tolist() if data[(data['Datetime'].dt.month == 4) & (data['Datetime'].dt.dayofweek == day - 1) & (data['Datetime'].dt.day > 21)].empty else (data[(data['Datetime'].dt.month == 4) & (data['Datetime'].dt.dayofweek == day - 1) & (data['Datetime'].dt.day > 21)]).astype(str).values.tolist()"
  ]
end

; Main simulation loop
to go
  ; Handle entry or exit events based on the current tick
  handle-entry-or-exit-event
  ; Increment the tick
  tick
end

; Procedure to handle entry or exit events based on the current tick
to handle-entry-or-exit-event
  ; Use "carefully" to handle potential runtime errors
  carefully [
    ; Get the row corresponding to the current tick from the data
    let row item ticks data
    ; Check if it's an entry event and generate students accordingly
    ifelse item 1 row = "Entry" [
      generate-entry-student
    ] [
      ; If it's not an entry event, generate an exit event
      generate-exit-student
    ]
    ; Set the current time based on the time in the data row
    set current-time time:create item 2 row
  ] [
    ; If an error occurs, stop the simulation
    stop
  ]
end

; Procedure to generate an entry student
to generate-entry-student
  ; Define levels for studying and discussion
  let study-levels ["3" "4" "5" "6" "6Chinese"]
  let discussion-levels ["3" "4"]
  ; Count the number of students with "chope" behavior
  let choped-seats count students with [current-behavior = "chope"]
  ; Generate a random probability
  let prob random-float 1
  ; Check if there are choped seats and choped students exist
  let choped-student-exists any? students with [current-behavior = "chope" and time:is-after? (current-time)  (time:plus time 30 "minutes")]
  ; If there are choped seats and choped students exist
  ifelse choped-seats != 0 and choped-student-exists [
    ; Ask one of the choped students to change behavior and reset appearance
    ask one-of students with [current-behavior = "chope" and time:is-after? (current-time)  (time:plus time 30.0 "minutes")] [
      set current-behavior initial-behavior
      set shape "person"
      set time current-time
    ]
  ] [
    ; If there are no choped seats or choped students, create a new student
    create-students 1 [
      set time current-time
      ; Generate a random probability
      let probability random-float 1
      ; Assign initial behavior based on probability
      if probability < study [
        set initial-behavior "study"
        set current-behavior "study"
      ]
      if probability >= study [
        set initial-behavior "discussion"
        set current-behavior "discussion"
      ]
      ; Set preferred floor based on current behavior
      if current-behavior = "study" [
        let pf one-of study-levels
        set preferred-floor pf
      ]
      if current-behavior = "discussion" [
        let pf one-of discussion-levels
        set preferred-floor pf
      ]
      ; Move the student to a patch on the preferred floor
      move-to one-of patches with [floor-number = [preferred-floor] of myself]
    ]
  ]
end

; Procedure to generate an exit student
to generate-exit-student
  ; Generate a random probability
  let probability random-float 1
  ; Check if there are students in the simulation
  if count students > 0 [
    ; If probability is less than or equal to the chope-seat probability
    ifelse probability <= chope-seat [
      ; Ask one of the students without "chope" behavior to chope a seat
      ask one-of students with [current-behavior !=  "chope"] [
        set current-behavior "chope"
        set shape "x"
        set time current-time
      ]
    ] [
      ; If probability is greater than chope-seat, ask one of the students to exit
      ask one-of students with [current-behavior != "chope"] [
        die
      ]
    ]
  ]
end

; Procedure to draw floors with specific attributes
to draw-floor [x y w l c f o]
  ask patches with
  [w + x > pxcor and pxcor >= x
    and
    pycor >= y and (y + l)> pycor ]
  [set pcolor c set floor-number f set max-occupancy o]
end

; Procedure to set up floors with specific attributes
to setup-floors
  ; Create patches for each floor and assign a floor number and max-occupancy
  draw-floor 1 2 24 24 white "3" 344
  draw-floor 1 28 24 24 white "4" 300
  draw-floor 28 2 24 24 white "5" 477
  draw-floor 28 28 24 24 white "6" 383
  draw-floor 55 18 15 15 white "6Chinese" 160
end
@#$#@#$#@
GRAPHICS-WINDOW
366
109
1084
658
-1
-1
10.0
1
15
1
1
1
0
0
0
1
0
70
0
53
1
1
1
ticks
30.0

BUTTON
34
234
97
267
setup
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
109
233
172
266
go
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
28
87
200
120
share-table
share-table
0
1
0.09
0.01
1
NIL
HORIZONTAL

SLIDER
24
142
196
175
chope-seat
chope-seat
0
1
0.1
0.01
1
NIL
HORIZONTAL

MONITOR
30
505
182
550
6Chinese occupancy rate
precision (count students with [preferred-floor = \"6Chinese\" and current-behavior != \"chope\"]/ 160) 3
17
1
11

MONITOR
29
391
138
436
5 occupancy rate
precision (count students with [preferred-floor = \"5\"] / 400) 3
17
1
11

CHOOSER
24
10
180
55
week
week
"Normal" "Exam" "Reading" "Recess"
0

CHOOSER
201
11
339
56
day
day
1 2 3 4 5 6 7
2

MONITOR
202
319
306
364
total_occupancy
count students with [current-behavior != \"chope\"]
17
1
11

MONITOR
210
445
301
490
current_time
time:show current-time \"HH:mm\"
17
1
11

BUTTON
199
232
302
265
go until close
go\ncarefully\n[let row item ticks data]\n[stop]
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

PLOT
45
565
325
805
occupancy
time
number-of-students
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot count students with [current-behavior != \"chope\"]"

MONITOR
207
383
301
428
chopped seats
count students with [current-behavior = \"chope\"]
17
1
11

SLIDER
29
186
201
219
study
study
0
1
0.87
0.01
1
NIL
HORIZONTAL

MONITOR
29
443
139
488
6 occupancy rate
precision (count students with [preferred-floor = \"6\" and current-behavior != \"chope\"]/ 383) 3
17
1
11

MONITOR
29
285
138
330
3 occupancy rate
precision (count students with [preferred-floor = \"3\" and current-behavior != \"chope\"]/ 344) 3
17
1
11

MONITOR
31
338
140
383
4 occupancy rate
precision (count students with [preferred-floor = \"4\" and current-behavior != \"chope\"]/ 300) 3
17
1
11

@#$#@#$#@
## WHAT IS IT?

This model simulates the behaviors of students in occupying space within the Central Library. Each square box represents a library level, starting from the bottom left to the right (3, 4, 5, 6, 6Chinese).

## HOW IT WORKS

Each tick in the model represents as minutes (sometimes hours), providing a temporal representation of student behaviors. Note that tick speed adjustments may be necessary while running the simulation.

## HOW TO USE IT

The model is designed to capture the dynamics of student behavior in the library. Adjust the parameters in the Interface tab to observe how different factors influence occupancy patterns. Key elements include entry and exit events, floor preferences, and student behaviors such as studying, discussions, and seat chope.

## THINGS TO NOTICE

Observe how the occupancy on each library level changes over time. Pay attention to patterns during peak hours and explore how different factors impact the overall occupancy.

## THINGS TO TRY

1. Adjust the tick speed to observe hourly changes more closely.
2. Experiment with the probability of students chope-ing seats.
3. Explore the impact of different entry and exit patterns on overall library occupancy.

## EXTENDING THE MODEL

1. Model out congestion at entry gates during different times of the day.
2. Implement more nuanced behaviors, such as the tendency to share tables.
3. Explore additional factors influencing student behaviors for a more accurate representation.

## NETLOGO FEATURES

The model utilizes NetLogo's time-based simulation features, including the use of ticks to represent hourly changes in the simulation.

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.3.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
