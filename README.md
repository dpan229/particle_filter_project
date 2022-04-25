# Particle Filter Project

## Group Members

David Pan, Max Lederman

## Implementation Plan

### initialize_particle_cloud

For this function, given a map of the maze, we will generate a randomly
sampled particle cloud that covers all of the empty spaces. We will test
our implementation using the `visualize_partices` program.

### update_particles_with_motion_model

To update the particle positions, we will move the particles in the same way
that we command the robot to move with some amount of noise added. To test
this, we will put many particles in one spot and see if the cloud resulting
from the motion model makes sense. 

### update_particle_weights_with_measurement_model

Given the current particle cloud and the measurements from the laser scan,
we would update the weights by simulating what the robot would see in each
particle's position and comparing it to the real measurements. We will test
this on a cloud with only a few particles in different positions and see if
the updated weights make sense.

### normalize_particles

To normalize the partices' importance weights, we will scale their weights
by the same factor so that their sum is 1. We will test this by checking the
sum of all of the particle weights before and after normalization.

### resample_particles

We will resample the particles by generating randomly selected particles from
the old population where the probability of choosing each particle is given
by its normalized weight. We will test this by doing runs with a small
number of particles.

### estimate_robot_pose

We will update the estimated pose of the robot by setting it to the particle
in the cloud that has the largest weight. We will test this by comparing it
to the real position of the robot.

### Incorporating Noise

We will incorporate noise into the motion model by making each particle move
and rotate slightly differently. We will also account for noise by averaging
the robot's laser scan readings with a few adjacent readings. We will
test our implentation of noise by putting many particles at one position and
seeing how they spread out over multiple steps.

### Timeline

Initializing particle cloud: Wed 4/13

Updating particles with motion model: Mon 4/18

Updating particle weights: Mon 4/18

Normalizing and resampling: Wed 4/20

Updating estimated pose: Fri 4/22

## Writeup

### Objectives

The main objective of this project was to implement a particle filter 
localization algorithm for determining the location of the robot given a map
of its environment and readings from its LiDAR and odometry. The robot is
steered around the environment via teleoperation, and as its sensors gather
more information, the particles converge on the robot's real location.

### High-level Description

To solve this project, we began by generating a cloud of particles across 
the maze. Every time the robot moves a certain distance, our particles move 
and turn based off the movement and then use the likelihood field method
to verify if the particle is valid. From there, we make sure to normalize 
our particles and resample them to regenerate an increasingly more accurate
cloud. Using this, as the particles converge, we can estimate where the robot
is located.


### Components

#### Initializing the particle cloud

Location: `ParticleFilter.initialize_particle_cloud` in particle_filter.py

Code description: Our implementation creates the initial particle cloud by
placing particles uniformly randomly around the vacant cells in the map with
uniformly random orientations.

#### The movement model

Location: `ParticleFilter.update_particles_with_motion_model` in particle_filter.py

Code description: Our implementation first rotates the particles, then moves
them forward or backward. The amount to move the particles is determined by
taking the distance the robot moved in the direction of the average between
its previous yaw and current yaw.

#### The measurement model

Location: `ParticleFilter.update_particle_weights_with_measurement_model` in particle_filter.py

Code description: We used the likelihood field method for this function.

#### Resampling the particles

Location: `ParticleFilter.resample_particles` in particle_filter.py

Code description: This function uses the `draw_random_sample` method. We draw
particles from the current particle cloud with probabilities equal to their
weights. In doing this, we make sure to use copies of each chosen particle 
instead of object references to avoid multiple particles in the cloud
pointing to the same object.

#### Incorporating noise

Location: `ParticleFilter.update_particles_with_motion_model` in particle_filter.py

Code description: Sets the yaw and linear position in accordance with the robot's 
movement multiplied by a randomly generated number between 0.9 and 1.1 to simulate 
a small amount of noise.

#### Updating the estimated robot pose

Location: `ParticleFilter.update_estimated_robot_pose` in particle_filter.py

Code description: Finds the average position and direction of all the particles 
generated. Takes into account the weight of each particle when generating the average.

#### Optimizing the parameters

Location: `ParticleFilter.update_particle_weights_with_measurement_model` in particle_filter.py
          `ParticleFilter.update_particles_with_motion_model` in particle_filter.py
          `ParticleFilter.__init__` in particle_filter.py
Code Description: Modified the impact of noise and size of the Gaussian standard
deviation to better suit the robot's inaccuracies. Dropped the number of particles
to 500 and scanned in increments of 15 degrees to optimize the code because it would lag
out using full particles and a complete scan. 

### Challenges
We faced two major challenges. The first was that we originally generated
our particle cloud in the wrong position, but by zooming out on RVIZ, we 
realized that we did not take into account the mazes origin for 
coordinates. The bigger problem, was that our particles would not converge 
around our robot's position. The movement of the particles was mostly in 
line with the robot though. To fix this, we first reduced the number of 
particles used to better see the movement of individual particles, then 
we tried adjusting noise and the Gaussian standard deviation values. Finally we 
realized that it was an error of using degrees instead of radians for
one of our values in our measurement model.

### Future work
If we had more time and much more powerful equipment, it would have been 
nice to run this project using more particles over a full 360 degrees
scan. In addition, with more time, we might have implemented the 
extra credit portion of the project, and tried to figure out how to get
our robot to move based off of position.

### Takeaways
1. This project helped a lot to improve our understanding of robot 
visualization within a fixed environment. Tracking how individual
particles move in line with the robot's movements and update based 
off of probabilities, we get a better feeling for how we can use 
python features to process an environment, which could be helpful
for the next project.
2. The other key takeaway was that this project forced us to use 
multiple functions in tandem. This goes both in the sense that we 
had to  operate our robot properly while using RVIZ to see the particles,
but also in the sense that this is the first time we had to code in 
robotics with so many different variables. This meant that a lot
more effort had to be put into debugging, first in identifying which function
had a problem, and then actually fixing the issue. 

### gif

![Particle filter gif](particle_filter_video.gif)
