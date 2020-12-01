---
title: "Moving In Occluded Environments"
excerpt: "When you can't see where you want to go<br/><img src='/images/research_pics/2020/occ_env/intro.png'>"
collection: portfolio
mathjax: true
---

### How do you move around a corner?

To a human, this question is pretty uninteresting. When we get to a corner, we either turn left or right and keep walking. When you think about, though, there is some nuance to this process. If we are running late, we may choose to cut the corner to reduce travel time. If there is a door right around the corner (like the elevator in the below picture), then we might move along the opposite wall in order get a good look at where we're going. What makes this process interesting is not knowing what is around the corner. For us, deciding how to move in the presence of occlusions comes from the kind of reasoning humans are naturally good at. For autonomous mobile robots (AMR), this is still an outstanding problem.

<br/><img width="460" height="300" src='/images/research_pics/2020/occ_env/intro.png'>

This research problem has two principle concerns that need to be addressed: safety and perception. One natural way of approaching this problem is to decompose these two principle concerns into questions that require different answers:
- How can the robot autonomously move to increase visibility around occlusions?
- How can the robot autonomously determine if it needs to gain visibility, or if it can safely cut around the occlusion?

My research effort was to answer these questions.

### Moving to increase visibility around occlusions

Typical control policies seek to track some reference that we give it. For autonomous robots, this reference is usually a waypoint that we want the robot to eventually reach. For this research, we also have the additional objective of minimizing occluded field of view. We call this occluded field of view the "known unknown area", shown below, and want the control policy to balance the two (sometimes conflicting) objectives of reference tracking and minimizing known unknown area.

<br/><img width="460" height="300" src='/images/research_pics/2020/occ_env/aku.png'>

This idea of "balancing" two different objectives is often tackled in optimal control theory. Optimal control theory seeks to find a control policy $\mathbf{u} = \pi(\mathbf{x})$ that can minimize a cost function $J(x,u)$. Reference tracking is often cast is as the square error $J_\text{ref} = (x - r)^2 $. Since the integrand is positive definite, this cost zero if and only if the system state $x$ exactly tracks the reference $r$. Physically, known unknown area is also positive definite, so if we had an analytical function $J_{ku}(x)$ to give us this area, we can create a combined objective function:

\begin{equation}
J(x,u) = J_\text{ref} + \phi_\text{ku}J_\text{ku}
\end{equation}

The scalar $\phi_\text{ku} = [0,\infty)$ determines the relative importance of reducing the known unknown area to the reference tracking objective. The bigger this scalar, the more important reducing occlusions becomes. If $\phi_\text{ku}=0$, then we don't care about reducing occlusions at all.

If system is currently in state $x_0$ and we have a model for how the system state $x$ changes with a control input $u$, we can predict future values of this cost function $J(x,u)$. Not only this, but we can also minimize the sum of this cost function over all predicted values:

\begin{equation}
\min_{u} \int J(x,u) dt
\end{equation}
\begin{equation*}
\text{s.t. x(t_0) = x_0}
\end{equation*}

This is called Model Predictive Control (MPC), and is an increasingly popular choice of controller not only because of its power, but also because computers are becoming good enough to provide control $u$ quickly enough for time-critical systems like UAVs.

