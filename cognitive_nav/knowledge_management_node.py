import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Recalibrado para entorno real (YOLO más ruidoso que en el simulador):
# mayor retención temporal suaviza detecciones intermitentes por oclusión/
# iluminación/ángulo. Steady-state de una zona vista de forma constante:
# 1/(1-DECAY) = 10.0.  (Simulador: 0.8 -> steady-state 5.0)
DECAY = 0.9


class KnowledgeManagementNode(Node):

    def __init__(self):
        super().__init__("knowledge_management_node")

        # Belief state
        # Solo las dos zonas del venue. "None" NO es una key: es el estado
        # por defecto que deduce el goal_manager cuando ninguna creencia
        # supera el umbral, no una hipótesis con creencia acumulada.
        self.room_beliefs = {
            "Casino": 0.0,
            "Classroom": 0.0,
        }

        # Subscribe to symbolic room inference
        self.subscription = self.create_subscription(
            String,
            "/symbolic/room_inference",
            self.callback,
            10,
        )

        # Publish belief state
        self.publisher = self.create_publisher(
            String,
            "/knowledge/beliefs",
            10,
        )

        self.get_logger().info("Knowledge Management Node initialized.")

    def callback(self, msg: String):
        """
        Called whenever the symbolic reasoner infers a room.
        """

        inferred_room = msg.data

        self.apply_decay()

        self.update_beliefs(inferred_room)

        self.publish_beliefs()

        self.print_beliefs()

    def update_beliefs(self, inferred_room):
        """
        Increase the belief associated with the inferred room.
        Example:
            LivingRoom += 1
        """
        if inferred_room in self.room_beliefs:
            self.room_beliefs[inferred_room] += 1.0
        else:
            self.get_logger().warn(
                f"Received unknown room category: '{inferred_room}'"
            )

    def apply_decay(self):
        """
        Apply memory decay to every room belief.
        Example:
            belief *= DECAY
        """
        for room in self.room_beliefs:
            self.room_beliefs[room] *= DECAY

    def publish_beliefs(self):
        """
        Publish the complete belief state as a JSON string.
        Hint:
            Use json.dumps().
        """
        msg = String()
        msg.data = json.dumps(self.room_beliefs)
        self.publisher.publish(msg)


    def print_beliefs(self):

        self.get_logger().info("Current beliefs:")

        for room, belief in self.room_beliefs.items():
            self.get_logger().info(
                f"  {room:12} {belief:.2f}"
            )


def main():

    rclpy.init()
    node = KnowledgeManagementNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
