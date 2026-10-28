import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


GOALS = [
    "Classroom",
    "Casino",
]

# Recalibrado para entorno real. Con DECAY=0.9 la creencia tras n detecciones
# consistentes es 10*(1-0.9^n):  n=2 -> 1.9,  n=3 -> 2.71,  n=4 -> 3.44.
# Un umbral de 2.5 exige ~3 detecciones consistentes, rechazando falsos
# positivos de 1-2 frames (ruido de YOLO). Ajustar en sitio si hace falta.
GOAL_THRESHOLD = 2.5


class GoalManagerNode(Node):

    def __init__(self):
        super().__init__("goal_manager_node")

        self.current_goal_index = 0

        self.subscription = self.create_subscription(
            String,
            "/knowledge/beliefs",
            self.callback,
            10,
        )

        self.get_logger().info("Goal Manager started.")

        self.print_goal()

    def callback(self, msg):

        beliefs = json.loads(msg.data)

        self.print_beliefs(beliefs)

        self.check_goal(beliefs)

    def recognized_zone(self, beliefs):
        """
        Zona reconocida = la de mayor creencia SIEMPRE que supere el umbral.
        Si ninguna lo supera, devuelve "None" (estado por defecto; no es una
        creencia acumulada, se deduce aquí).
        """
        if not beliefs:
            return "None"
        zone, belief = max(beliefs.items(), key=lambda kv: kv[1])
        return zone if belief >= GOAL_THRESHOLD else "None"

    def check_goal(self, beliefs):
        """
        Determine whether the current goal has been achieved.
        """
        if self.current_goal_index >= len(GOALS):
            # No hay goal activo, la misión ya terminó
            return

        current_goal = GOALS[self.current_goal_index]
        belief = beliefs.get(current_goal, 0.0)
        zone = self.recognized_zone(beliefs)

        self.get_logger().info(
            f"Perceived zone: {zone} | goal: {current_goal} "
            f"(belief={belief:.2f} / thr={GOAL_THRESHOLD})"
        )

        # Caso "None": ninguna zona supera el umbral -> seguir esperando.
        # NO se avanza el índice de metas (evita saltos por falta de evidencia).
        if zone == "None":
            self.get_logger().info("No zone confirmed yet -> waiting")
            return

        # La meta solo se cumple si la zona reconocida con confianza ES la meta
        # actual (evita avanzar por estar en la zona equivocada).
        if zone == current_goal and belief >= GOAL_THRESHOLD:
            self.get_logger().info(f"Goal achieved: {current_goal}")
            self.next_goal()
        else:
            self.get_logger().info(f"Still pursuing: {current_goal}")


    def next_goal(self):
        """
        Activate the next goal.
        """
        self.current_goal_index += 1
        self.print_goal()


    def print_goal(self):
        """
        Print the current active goal.
        """
        if self.current_goal_index < len(GOALS):
            self.get_logger().info(
                f"Active goal: {GOALS[self.current_goal_index]}"
            )
        else:
            self.get_logger().info("Mission completed! All goals achieved.")

    def print_beliefs(self, beliefs):

        self.get_logger().info("Beliefs:")

        for room, belief in beliefs.items():
            self.get_logger().info(
                f"  {room:12} {belief:.2f}"
            )


def main():

    rclpy.init()

    node = GoalManagerNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
