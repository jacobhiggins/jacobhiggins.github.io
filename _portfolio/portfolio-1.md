---
title: "Moving In Occluded Environments"
# excerpt: "When you can't see where you want to go<br/><img src='/images/research_pics/2020/occ_env/intro.png'>"
excerpt: "When you can't see where you want to go"
collection: portfolio
mathjax: true
---
<style>
.column {
  float: left;
  width: 50%;
  padding: 5px;
}

/* Clear floats after image containers */
.row::after {
  content: "";
  clear: both;
  display: table;
}
</style>

### How do you move around a corner?

To a human, this question is pretty uninteresting. When we get to a corner, we either turn left or right and keep walking. When you think about, though, there is some nuance to this process. If we are running late, we may choose to cut the corner to reduce travel time. If there is a door right around the corner (like the elevator in the below picture), then we might move along the opposite wall in order get a good look at where we're going. What makes this process interesting is not knowing what is around the corner. For us, deciding how to move in the presence of occlusions comes from the kind of reasoning humans are naturally good at. For autonomous mobile robots (AMR), this is still an outstanding problem.

<p align="center">
  <img width="460" height="300" src='/images/research_pics/2020/occ_env/intro.png'>
</p>

This research problem has two principle concerns that need to be addressed: safety and perception. One natural way of approaching this problem is to decompose these two principle concerns into questions that require different answers:
- How can the robot autonomously move to increase visibility around occlusions?
- How can the robot autonomously determine if it needs to gain visibility, or if it can safely cut around the occlusion?

My research effort was to answer these questions.

### Moving to increase visibility around occlusions

Typical control policies seek to track some reference that we give it. For autonomous robots, this reference is usually a waypoint that we want the robot to eventually reach. For this research, we also have the additional objective of minimizing occluded field of view. We call this occluded field of view the "known unknown area", shown below, and want the control policy to balance the two (sometimes conflicting) objectives of reference tracking and minimizing known unknown area.

<p align="center">
  <img width="460" height="300" src='/images/research_pics/2020/occ_env/aku.png'>
</p>

This idea of "balancing" two different objectives is often tackled in optimal control theory. Optimal control theory seeks to find a control policy $\mathbf{u} = \pi(\mathbf{x})$ that can minimize a cost function $J(\mathbf{x},\mathbf{u})$. Reference tracking is often cast is as the square error $J_\text{ref} = (\mathbf{x} - \mathbf{r})^2 $. Since the integrand is positive definite, this cost zero if and only if the system state $\mathbf{x}$ exactly tracks the reference $\mathbf{r}$. Physically, known unknown area is also positive definite, so if we had an analytical function $J_{ku}(\mathbf{x})$ to give us this area, we can create a combined objective function:

\begin{equation}
J(\mathbf{x},\mathbf{u}) = J_\text{ref} + \phi_\text{ku}J_\text{ku}
\end{equation}

The scalar $\phi_\text{ku} = [0,\infty)$ determines the relative importance of reducing the known unknown area to the reference tracking objective. The bigger this scalar, the more important reducing occlusions becomes. If $\phi_\text{ku}=0$, then we don't care about reducing occlusions at all.

If system is currently in state $\mathbf{x}_0$ and we have a model for how the system state $x$ changes with a control input $u$, we can predict future values of this cost function $J(\mathbf{x},\mathbf{u})$. Not only this, but we can also minimize the sum of this cost function over all predicted values:

\begin{equation}
\min\_{\mathbf{u}} \int J(\mathbf{x},\mathbf{u}) dt
\end{equation}
\begin{equation\*}
\text{s.t.} \mathbf{x}(t\_{0}) = \mathbf{x}\_{0}
\end{equation\*}

This is called Model Predictive Control (MPC), and is an increasingly popular choice of controller not only because of its ability to handle complex MIMO systems near constraints, but also because computers are now becoming good enough to provide control $\mathbf{u}$ quickly for time-critical systems like UAVs.

For the control policy I designed, the reference tracking objective $J_\text{ref}(\mathbf{x},\mathbf{u})$ was a simple square error between a current system state $\mathbf{x}$ and a waypoint location $r$ that helped steer the robot towards the goal. Defining the perception objective was harder, because a general expression for the known-unknown area has discontinuities in derivatives for different hallway shapes. This discontinuity presented problems with the optimization software we selected to use. Instead, I found simple analytic expression that approximated the true value for the known-unknown area:

\begin{equation}
J\_{ku}(\mathbf{x}) = \frac{\text{arctan}(\theta)}{\Delta y} = \frac{\text{arctan}(\Delta y/\Delta x)}{\Delta y}
\end{equation}

This perception objective $J_{ku}(\mathbf{x})$ was defined in terms of the robot's relative location to the corner $\Delta x$ and $\Delta y$ (shown in Fig. 2 above). This expression is simple to evaluate in an optimizer, and has two key properties:

\begin{equation} \label{eq:perc-obj-far}
\lim_{\Delta y\rightarrow \infty}J_{ku}(\mathbf{x}) = 0
\end{equation}
\begin{equation}\label{eq:perc-obj-close}
\lim_{\Delta y\rightarrow 0}J_{ku}(\mathbf{x}) = 1/\Delta x
\end{equation}

In English, Eq. \ref{eq:perc-obj-far} shows how the perception objective vanishes when the robot is far away from the occluding corner, and Eq. \ref{eq:perc-obj-close} shows that perception objective approaches a value of $1/\Delta x$ when close to the occluding corner. In this case, the optimizer will try to increase $\Delta x$ in order to decrease the perception objective, thus moving the robot away form the occluding corner. Below shows the resulting motion when including the perception objective inside the MPC controller:

<p align="center">
  <img width="460" height="300" src="/images/research_pics/2020/occ_env/res2.png">
</p>

And here is a graph that shows how the known-unknown area is reduced when using the perception objective:

<p align="center">
  <img width="460" height="300" src="/images/research_pics/2020/occ_env/re2.png">
</p>

### Placing the waypoint when the robot is in a safe environment

Assuming we can identify the location of an occluding corner, the perception objective allows the MPC to move so that it can reduce the known-unknown area produced by the occluding corner. The next step is to determine where to place the reference $\mathbf{r}$, which I will refer to as the waypoint. This waypoint must produce smooth, continuous motion in the robot in different situations. The first situation we'll consider is when $\phi_{ku}=0$, i.e., when the robot system doesn't care to reduce occluded vision. In this case, we want the robot to cut the occluding corner, as this would minimize the overall travel time.

In order to do this, we assume that the overall layout of the environment is known a priori. This only refers to walls and other permanent structures, and not obstacles that can move. In this way, we can create a very simple reference trajectory $\tau$ that can loosely guide the robot through the corridors. By considering the edge of the area visible to the robot $\delta A_{s}$, we place the waypoint at the intersection of these two lines:

\begin{equation}
\mathbf{r} = \delta A_{s} \cap \tau
\end{equation}

Fig. () below shows visible area $\delta A_{s}$, reference trajectory $\tau$ and the intersection of these two lines as $p^*_\tau$ (ignore the other points for now). By placing the waypoint $\mathbf{r}$ where the edge of the visible area intersects the reference trajectory, we ensure that the robot will only move in a direction directly in its line of sight, cutting the corner when possible. Below shows the motion of the robot following this waypoint. Notice how it can cut the corner, reducing overall traveling time:

<div class="row">
  <div class="column">
    <img src="/images/research_pics/2020/occ_env/res33.png" alt="Snow" style="width:50%">
  </div>
  <div class="column">
    <img src="/images/research_pics/2020/occ_env/re3.png" alt="Forest" style="width:50%">
  </div>
</div>

Again, this motion is only desirable when we know nothing is around the corner, or $\phi_{ku}=0$. On the other hand, motion with a nonzero perception weight $\phi_{ku}$ is desirable when we wish to see more around the corner. How can the robot autonomously decide between these two options?

### Using probability of collision to decide motion

In order to autonomously make this decision, I focused on a similar, more mathematically manageable question: is the robot expected to collide with a dynamic obstacle?

This question is answered using probability theory, and requires a model for the probability of collision in terms of position in the world. The key to finding this probability model is realizing that the probability of colliding with an obstacle at point $\bar{\mathbf{x}}$ is the same probability of an obstacle occupying that same point $\bar{\mathbf{x}}$. This may sound obvious, but this connection is what allows me to tap into a well-studied probability model known as (occupancy grid mapping)[https://en.wikipedia.org/wiki/Occupancy_grid_mapping]. In an occupancy grid, the entire environment is discretized into a grid where each square contains a value for the probability of occupancy, denoted as $P(x)$. When $P(x)=1$, then an object is known to be occupying that grid space, and when $P(x)=0$ then it is equally certain that there is nothing occupying that grid space.

The image below shows a simple, one dimensional occupancy grid map. The grayer the grid, the higher the probability that an obstacle is occupying that location. In this one dimensional world, the future trajectory of the car is to the right, toward these areas of uncertainty. So, there is some likelihood that the car will crash at certain distances as it travels to the right.

<p align="center">
  <img width="460" height="300" src="/images/research_pics/2020/occ_env/future_motion_grid.png">
</p>

If we let the car run and crash a million times, the exact location of the crash will obviously be different each time. But if took those distances and averaged them, we would get what is called _expected value_ for the distance traveled until collision. This expected distance to collision gives an estimate on how far the car can travel before it expects to hit something. To determine safety, we compare the expected distance to collision to the distance required for the system to stop. This stopping distance is an intrinsic property of the robot, dependent on things like much mass the robot and how hard it can brake. Below is the same figure, showing an example of the stopping distance and expected distance to collision:

<p align="center">
  <img width="460" height="300" src="/images/research_pics/2020/occ_env/crash_stop_grid.png">
</p>

Here, the stopping distance is less than the expected distance to collision, meaning the robot has the ability to stop before colliding. If, however, the stopping distance was larger than the expected distance to collision, then the robot would likely collide with an obstacle. By comparing these two distances, our control framework can determine if a waypoint is safe or unsafe.

### Combining safety and perception

When moving around a corner, the main source of uncertainty is the fact that the robot cannot see around the corner, and accidentally run into something it cannot see. This increases the chance of collisions, and thus decreases the expected distance to collision as we approach the corner. If this is the case, then we can use the MPC we defined above to help the robot move around the corner, gaining visibility and reducing over all uncertainty. Doing so results in more certainty moving around the corner is safe, increasing the expected distance to collision.

Our control framework continually answer these two questions:
- Question 1: Is the expected distance to collision less than the stopping distance? (Safety)
- Question 2: If the expected distance to collision is less than the stopping distance and the situation is unsafe, what is the optimal trajectory to reduce occlusions (Visibility), thereby increasing safety?

The previous sections detail how both of these questions are answered. Next, let's look at some simulations that use the proposed control framework.

### Simulations

So, what does the full control framework look like? Below is a gif of an example situation, where an unmanned ground vehicle (UGV) is approaching an occluding corner. There is a lot of things going on in this one gif, so here's a break down of the important components:
- Big blue dot: simulated UGV
- Lots of tiny blue dots: simulated dynamic objects (e.g. people, other robots), moving from right to left with some set velocity profile
- Orange dashed line: field of view of the UGV sensors
- Red-dashed line: reference trajectory
- Pink area around corner: area occluded to UGV (in my paper I call this the known unknown area)
- Gray area in second hallway: probability of occupancy in over a discretized grid in the second hallway (more gray = higher probability)

The rest is self-explanatory. So, what is happening? At the beginning of the simulation, the robot moves down the hallway unaware of the corner. Once the corner is within field of view, the robot is uncertain of what is around the corner and so moves to get a better look. At first, the expected distance to collision is longer than the breaking distance past the corner. The more the UGV observes what it can around the corner, the more it is certain that nothing is occupying the second hallway; hence, the observed area becomes whiter. At a certain point (around 4.2 seconds) the expected distance to collision becomes shorter than the breaking distance. At this point, it is safe to move into the second hallway and the robot begins to cut the corner.

![Value Iteration Value Function](/images/research_pics/2020/occ_env/control_framework.gif)

All the tiny blue dots are meant to represent all the locations that a moving object might be as they move from right to left. Once a tiny blue dot comes within the FOV of the UGV, we consider that the object was observed by the UGV (in the sim, they disappear). Each time a tiny blue dot is observed, we record the distance between the dot and the robot. In general, the closer the object is first observed by the UGV, the more percarious the situation, since the robot doesn't have as much time to react. For comparison, consider the simulation below where the robot simply cuts the corner:

![Value Iteration Value Function](/images/research_pics/2020/occ_env/cut_corner.gif)

By cutting the corner, the UGV reduces overall travel time. But notice how as it cuts the corner, there are many dynamic objects/blue dots that are coming around the corner as well, still unobserved by the robot. As the objects come into view, the UGV may observe these people, but is going too fast to slow down.

By recording the distances-at-first-sight between UGV and simulated people, we can get a sense of how safe each robot motion is. Below shows a cumulative distribution function of these recorded distances:

<p align="center">
  <img width="500" height="320" src="/images/research_pics/2020/occ_env/safety-results.png">
</p>

Unlike probability functions, where a function $p(x)$ gives you the probability of obtaining $x$, a cumulative distribution function $CDF(x)$ gives you the probability of obtaining a value _less than or equal to_ $x$. This CDF is well-suited for our application, since we want to know the probability of first observing a dynamic object within a certain distance (i.e., less that or equal to a distance). In the figure above, you see that the CDF reaches a value of one at 5 meters. This is the maximum sensing range for the UGV, and simply means that the UGV must observe dynamic object within 5 meters, since it can't see outside its range.

On this plot are three different runs. The blue bars correspond to the robot simply cutting the corner, and the yellow bars are when the robot uses the full control framework, moving to gain visibility then cutting the corner when its safe. The brown-ish bar is a third run that is "in between," since it doesn't cut the corner, but it also doesn't move to gain visibility. It slows down before entering the second hallway (staying in the middle of the first hallway), and only enters when it sees no one is coming around the corner.

