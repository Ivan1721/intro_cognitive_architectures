# Copyright 2026 — Solo los nodos cognitivos (sin YOLO, sin simulador).
#
# Arranca la capa de razonamiento: symbolic -> knowledge -> goal.
# Asume que ALGO ya publica /yolo/detections_3d (p. ej. yolo.launch.py aparte,
# o mirte_real.launch.py que trae YOLO + estos nodos juntos).
#
#   ros2 launch cognitive_nav cognitive.launch.py

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time", default_value="false",
        description="Robot real -> false (usa true solo si corres contra Gazebo)",
    )

    common = [{"use_sim_time": use_sim_time}]

    symbolic = Node(
        package="cognitive_nav", executable="symbolic_node",
        name="symbolic_node", output="screen", parameters=common,
    )
    knowledge = Node(
        package="cognitive_nav", executable="knowledge_management_node",
        name="knowledge_management_node", output="screen", parameters=common,
    )
    goal = Node(
        package="cognitive_nav", executable="goal_manager_node",
        name="goal_manager_node", output="screen", parameters=common,
    )

    return LaunchDescription([use_sim_time_arg, symbolic, knowledge, goal])
