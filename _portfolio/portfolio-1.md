---
title: "Moving In Occluded Environments"
excerpt: "When you can't see where you want to go<br/><img width="460" height="300" src='/images/research_pics/2020/occ_env/intro.png'>"
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

### How can a robot autonomously move to increase visibility around occlusions?

