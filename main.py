
from drafter import *
from dataclasses import dataclass
import matplotlib.pyplot as plt
import math
set_website_title("Euler Cromer Method")
set_site_information(
    author="Claudia Hensil",
    description="Guides students through Euler Cromer Method",
    sources="LLM Drafter Communication.pdf",
    planning=["CS1 Final Project 1: Design.pdf", "CS1 Final Project 0: Pick a Problempdf"],
    links=["https://github.com/c-hensil/euler-cromer-method"]
)
hide_debug_information()
set_website_framed(False)
# Distance represents a displacement value
Distance = float


@dataclass
class Calculations:
    distance: float
    time: float


@dataclass
class State:
    # Requested attributes
    displacement: list[Distance]
    velocity_current: float
    momentum_current: float
    net_force: float

    # Additional information needed
    times: list[float]
    mass: float
    delta_t: float
    total_steps: int
    current_step: int

    # Keep track of every calculation
    momentum_history: list[float]
    velocity_history: list[float]
    calculations: list[Calculations]

    # Wrong answer page information
    expected_answer: float
    submitted_answer: float
    retry_route: str


# --------------------------------
# Starting page
# --------------------------------

@route
def index(state: State,
          initial_position: float = None,
          initial_velocity: float = None,
          mass: float = None,
          net_force: float = None,
          delta_t: float = None,
          steps: int = None) -> Page:

    if initial_position is None:
        return Page(state, [
            Header("Euler-Cromer Simulator"),
            "Enter the initial conditions of your particle.",
            "Initial displacement:",
            TextBox("initial_position"),
            "Initial velocity:",
            TextBox("initial_velocity"),
            "Mass:",
            TextBox("mass"),
            "Net force:",
            TextBox("net_force"),
            "Time interval (delta t):",
            TextBox("delta_t"),
            "Number of iterations:",
            TextBox("steps"),
            Button("Start calculations", "index")
        ])

    # Check basic input requirements
    if mass <= 0 or delta_t <= 0 or steps <= 0:
        return Page(state, [
            Header("Invalid input"),
            "Mass, time interval, and steps must be positive.",
            Button("Go back", "index")
        ])

    # Calculate initial momentum
    initial_momentum = mass * initial_velocity

    # Create a fresh simulation
    state.displacement = [initial_position]
    state.times = [0.0]
    state.velocity_current = initial_velocity
    state.momentum_current = initial_momentum
    state.net_force = net_force

    state.mass = mass
    state.delta_t = delta_t
    state.total_steps = steps
    state.current_step = 0

    state.momentum_history = [initial_momentum]
    state.velocity_history = [initial_velocity]
    state.calculations = []

    return calculate_momentum(state)


# --------------------------------
# Step 1: Momentum
# --------------------------------

@route
def calculate_momentum(state: State,
                       answer: float = None) -> Page:

    expected = (state.momentum_current
                + state.net_force * state.delta_t)

    if answer is not None:
        if not math.isclose(answer, expected,
                            rel_tol=1e-6, abs_tol=1e-6):
            state.expected_answer = expected
            state.submitted_answer = answer
            state.retry_route = "calculate_momentum"
            return wrong_answer(state)

        state.momentum_current = expected
        state.momentum_history.append(expected)
        return Update_velocity(state)

    return Page(state, [
        Header("Step 1: Calculate Momentum"),
        "Iteration: " + str(state.current_step + 1),
        "Initial momentum: " + str(state.momentum_current),
        "Net force: " + str(state.net_force),
        "Time interval: " + str(state.delta_t),
        "Calculate final momentum:",
        "p final = p initial + (F * delta t)",
        TextBox("answer"),
        Button("Check momentum", "calculate_momentum")
    ])


# --------------------------------
# Step 2: Velocity
# --------------------------------

@route
def Update_velocity(state: State,
                    answer: float = None) -> Page:

    expected = state.momentum_current / state.mass

    if answer is not None:
        if not math.isclose(answer, expected,
                            rel_tol=1e-6, abs_tol=1e-6):
            state.expected_answer = expected
            state.submitted_answer = answer
            state.retry_route = "Update_velocity"
            return wrong_answer(state)

        state.velocity_current = expected
        state.velocity_history.append(expected)
        return Update_distance(state)

    return Page(state, [
        Header("Step 2: Calculate Velocity"),
        "Final momentum: " + str(state.momentum_current),
        "Mass: " + str(state.mass),
        "Calculate final velocity:",
        "v final = p final / mass",
        TextBox("answer"),
        Button("Check velocity", "Update_velocity")
    ])


# --------------------------------
# Step 3: Displacement
# --------------------------------

@route
def Update_distance(state: State,
                    answer: float = None) -> Page:

    expected = (state.displacement[-1]
                + state.velocity_current * state.delta_t)

    if answer is not None:
        if not math.isclose(answer, expected,
                            rel_tol=1e-6, abs_tol=1e-6):
            state.expected_answer = expected
            state.submitted_answer = answer
            state.retry_route = "Update_distance"
            return wrong_answer(state)

        state.displacement.append(expected)
        return Update_time(state)

    return Page(state, [
        Header("Step 3: Calculate Displacement"),
        "Initial displacement: " + str(state.displacement[-1]),
        "Final velocity: " + str(state.velocity_current),
        "Time interval: " + str(state.delta_t),
        "Calculate final displacement:",
        "x final = x initial + (v final * delta t)",
        TextBox("answer"),
        Button("Check displacement", "Update_distance")
    ])


# --------------------------------
# Step 4: Time
# --------------------------------

@route
def Update_time(state: State,
                answer: float = None) -> Page:

    expected = state.times[-1] + state.delta_t

    if answer is not None:
        if not math.isclose(answer, expected,
                            rel_tol=1e-6, abs_tol=1e-6):
            state.expected_answer = expected
            state.submitted_answer = answer
            state.retry_route = "Update_time"
            return wrong_answer(state)

        state.times.append(expected)

        # Save matching distance and time values
        state.calculations.append(
            Calculations(
                distance=state.displacement[-1],
                time=expected
            )
        )

        state.current_step += 1

        if state.current_step < state.total_steps:
            return calculate_momentum(state)

        return Create_graph(state)

    return Page(state, [
        Header("Step 4: Update Time"),
        "Initial time: " + str(state.times[-1]),
        "Time interval: " + str(state.delta_t),
        "Calculate final time:",
        "t final = t initial + delta t",
        TextBox("answer"),
        Button("Check time", "Update_time")
    ])


# --------------------------------
# Wrong answer page
# --------------------------------

@route
def wrong_answer(state: State) -> Page:

    return Page(state, [
        Header("Not quite!"),
        "Your answer: " + str(state.submitted_answer),
        "Calculated answer: " + str(state.expected_answer),
        "Review the equation and try again.",
        Button("Try again", state.retry_route)
    ])


# --------------------------------
# Step 5: Create Graph
# --------------------------------

@route
def Create_graph(state: State) -> Page:

    plt.figure()
    plt.plot(state.times, state.displacement, marker="o")
    plt.xlabel("Time")
    plt.ylabel("Displacement")
    plt.title("Particle Trajectory")
    plt.grid(True)

    return Page(state, [
        Header("Particle Trajectory"),
        "You completed all the Euler-Cromer calculations!",
        "Here is your displacement versus time graph.",
        MatPlotLibPlot(),
        Button("Continue to full method", "Show_method")
    ])


# --------------------------------
# Step 6: Show the full method
# --------------------------------

@route
def Show_method(state: State) -> Page:

    process = []

    for i in range(state.total_steps):
        process.append(
            "Iteration " + str(i + 1) + "\n"
            + "Momentum: "
            + str(state.momentum_history[i + 1]) + "\n"
            + "Velocity: "
            + str(state.velocity_history[i + 1]) + "\n"
            + "Displacement: "
            + str(state.calculations[i].distance) + "\n"
            + "Time: "
            + str(state.calculations[i].time)
        )

    return Page(state, [
        Header("Complete Euler-Cromer Method"),
        "Initial conditions:",
        "Mass: " + str(state.mass),
        "Net force: " + str(state.net_force),
        "Time interval: " + str(state.delta_t),
        "Initial velocity: " + str(state.velocity_history[0]),
        "Initial displacement: " + str(state.displacement[0]),
        Header("Calculation History"),
        BulletedList(process),
        Button("Start Over", "index")
    ])


# --------------------------------
# Start the website
# --------------------------------

start_server(
    State(
        displacement=[],
        velocity_current=0.0,
        momentum_current=0.0,
        net_force=0.0,
        times=[],
        mass=1.0,
        delta_t=0.1,
        total_steps=1,
        current_step=0,
        momentum_history=[],
        velocity_history=[],
        calculations=[],
        expected_answer=0.0,
        submitted_answer=0.0,
        retry_route="index"
    )
)

