#!/usr/bin/env python3

import rospy

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, PoseArray, Pose, Point, Quaternion
from nav_msgs.srv import GetMap
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header, String

from likelihood_field import LikelihoodField

import math
import numpy as np
from tf.transformations import quaternion_from_euler, euler_from_quaternion


def compute_prob_zero_centered_gaussian(dist, sd):
    """ Takes in distance from zero (dist) and standard deviation (sd) for gaussian
        and returns probability (likelihood) of observation """
    c = 1.0 / (sd * math.sqrt(2 * math.pi))
    prob = c * math.exp((-math.pow(dist,2))/(2 * math.pow(sd, 2)))
    return prob


class Particle:

    def __init__(self, pose, w):
        self.pose = pose
        self.w = w

    def __str__(self):
        theta = euler_from_quaternion([
            self.pose.orientation.x, 
            self.pose.orientation.y, 
            self.pose.orientation.z, 
            self.pose.orientation.w])[2]
        return ("Particle: [" + str(self.pose.position.x) + ", " + str(self.pose.position.y) + ", " + str(theta) + "]")


class LikelihoodFieldMeasurementUpdate(object):


    def __init__(self):

        # once everything is setup initialized will be set to true
        self.initialized = False   

        # initalize node
        rospy.init_node('turtlebot3_likelihood_field_measurement_update')

        # subscribe to the map server
        self.map_topic = "map"
        rospy.Subscriber(self.map_topic, OccupancyGrid, self.get_map)

        # subscribe to the lidar scan from the robot
        rospy.Subscriber("scan", LaserScan, self.robot_scan_received)

        # publish the current particle cloud.  This enables viewing particles in rviz.
        self.particles_pub = rospy.Publisher("particlecloud", PoseArray, queue_size=10)

        # inialize our map and likelihood field
        self.map = OccupancyGrid()
        self.likelihood_field = LikelihoodField()

        self.particle_cloud = []

        self.initialize_particle_cloud()

        self.initialized = True


    def initialize_particle_cloud(self):

        # we'll initialize these 4 particles of form [x, y, theta]
        initial_particle_set = [
            [0.0, 0.0, 0.0],
            [-6.6, -3.5, np.pi],
            [5.8, -5.0, (np.pi / 2.0)],
            [-2.0, 4.5, (np.pi * 3.0 / 2.0)]
        ]

        self.particle_cloud = []


        for i in range(len(initial_particle_set)):
            p = Pose()
            p.position = Point()
            p.position.x = initial_particle_set[i][0]
            p.position.y = initial_particle_set[i][1]
            p.position.z = 0
            p.orientation = Quaternion()
            q = quaternion_from_euler(0.0, 0.0, initial_particle_set[i][2])
            p.orientation.x = q[0]
            p.orientation.y = q[1]
            p.orientation.z = q[2]
            p.orientation.w = q[3]

            # initialize the new particle, where all will have the same weight (1.0)
            new_particle = Particle(p, 1.0)

            # append the particle to the particle cloud
            self.particle_cloud.append(new_particle)

        self.publish_particle_cloud()



    def get_map(self, data):
        # store the map data
        self.map = data


    def publish_particle_cloud(self):

        particle_cloud_pose_array = PoseArray()
        particle_cloud_pose_array.header = Header(stamp=rospy.Time.now(), frame_id=self.map_topic)
        particle_cloud_pose_array.poses

        for part in self.particle_cloud:
            particle_cloud_pose_array.poses.append(part.pose)

        self.particles_pub.publish(particle_cloud_pose_array)


    def robot_scan_received(self, data):

        # wait until initialization is complete
        if not(self.initialized):
            return

        direction_idxs = range(360)

        # Compute the importance weights (w) for the 4 particles 
        # in this environment using the likelihood field measurement
        # algorithm.

        for particle in self.particle_cloud:
            # get particle position and angle
            particle_x = particle.pose.position.x
            particle_y = particle.pose.position.y
            particle_theta = euler_from_quaternion(particle.pose.orientation.x,
                                                   particle.pose.orientation.y,
                                                   particle.pose.orientation.z,
                                                   particle.pose.orientation.w)[2]
            # get product of gaussian likelihoods for each distance reading
            q = 1.0
            for scan_direction in cardinal_directions_idxs:
                scan_end_x = particle_x + data.ranges[scan_direction] * np.cos(particle_theta + scan_direction)
                scan_end_y = particle_y + data.ranges[scan_direction] * np.sin(particle_theta + scan_direction)
                dist = self.likelihood_field.get_closest_obstacle_distance(scan_end_x, scan_end_y)
                # use standard deviation 0.1
                q *= compute_prob_zero_centered_gaussian(dist, 0.1)
            # set weight to likelihood
            particle.w = q

    def run(self):
        r = rospy.Rate(1)
        while not rospy.is_shutdown():
            self.publish_particle_cloud()
            r.sleep()



if __name__ == '__main__':

    node = LikelihoodFieldMeasurementUpdate()
    node.run()