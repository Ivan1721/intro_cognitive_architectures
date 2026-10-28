# Copyright 2026 — Cognitive nav on the REAL Mirte Master (no Gazebo)
#
# Lanza el pipeline cognitivo (YOLO 3D -> symbolic -> knowledge -> goal) contra
# el robot físico. NO arranca simulador. Los topics de cámara son argumentos:
# verifícalos con `ros2 topic list` cuando el robot esté conectado y ajústalos
# si difieren de los valores por defecto (tomados del simulador).
#
#   ros2 launch cognitive_nav mirte_real.launch.py \
#       input_image_topic:=/rgbd_camera/image \
#       input_depth_topic:=/rgbd_camera/depth_image \
#       input_depth_info_topic:=/rgbd_camera/camera_info

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    ExecuteProcess,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    image_topic = LaunchConfiguration("input_image_topic")
    depth_topic = LaunchConfiguration("input_depth_topic")
    depth_info_topic = LaunchConfiguration("input_depth_info_topic")
    target_frame = LaunchConfiguration("target_frame")
    model = LaunchConfiguration("model")
    device = LaunchConfiguration("device")
    park_arm = LaunchConfiguration("park_arm")

    args = [
        DeclareLaunchArgument(
            "use_sim_time", default_value="false",
            description="Robot real -> false",
        ),
        # --- Topics de la cámara de profundidad REAL (VERIFICAR al conectar) ---
        DeclareLaunchArgument(
            "input_image_topic", default_value="/rgbd_camera/image",
            description="Topic de imagen RGB de la cámara de profundidad",
        ),
        DeclareLaunchArgument(
            "input_depth_topic", default_value="/rgbd_camera/depth_image",
            description="Topic de imagen de profundidad",
        ),
        DeclareLaunchArgument(
            "input_depth_info_topic", default_value="/rgbd_camera/camera_info",
            description="Topic camera_info de la cámara de profundidad",
        ),
        DeclareLaunchArgument(
            "target_frame", default_value="camera_link",
            description="Frame al que se transforman las cajas 3D",
        ),
        DeclareLaunchArgument(
            "model",
            default_value="/home/ubuntu-user/mirte_ws/src/"
            "intro_cognitive_architectures/yolov8m.pt",
            description="Ruta a los pesos YOLO",
        ),
        DeclareLaunchArgument(
            "device", default_value="cuda:0",
            description="cuda:0 (GPU) o cpu",
        ),
        DeclareLaunchArgument(
            "park_arm", default_value="true",
            description="Mover el brazo fuera del campo de visión al inicio",
        ),
    ]

    # --- Percepción: YOLO con detecciones 3D + tracking ---
    yolo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("yolo_bringup"), "launch", "yolo.launch.py"]
            )
        ),
        launch_arguments={
            "model": model,
            "device": device,
            "input_image_topic": image_topic,
            "input_depth_topic": depth_topic,
            "input_depth_info_topic": depth_info_topic,
            "target_frame": target_frame,
            "use_3d": "True",
            "use_tracking": "True",
        }.items(),
    )

    # --- Nodos cognitivos (representación -> razonamiento -> gestión de metas) ---
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

    # --- Sacar el brazo del campo de visión (opcional) ---
    park = TimerAction(
        period=3.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    "ros2", "topic", "pub", "--once",
                    "/mirte_master_arm_controller/joint_trajectory",
                    "trajectory_msgs/msg/JointTrajectory",
                    "{joint_names: [shoulder_pan_joint, shoulder_lift_joint, "
                    "elbow_joint, wrist_joint], points: [{positions: "
                    "[0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 2}}]}",
                ],
                output="screen",
            )
        ],
        condition=IfCondition(park_arm),
    )

    return LaunchDescription(args + [yolo, symbolic, knowledge, goal, park])
