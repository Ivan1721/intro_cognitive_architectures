from owlready2 import *


def load_ontology():
    """
    Ontología para un venue real tipo escuela/oficina.

    Dos zonas objetivo: Casino (comedor/cafetería) y Classroom (aula).
    La clasificación de una zona exige combinaciones de AL MENOS 2 objetos
    para evitar ambigüedad: una silla (chair) aparece en ambas zonas, así que
    nunca decide por sí sola. Los discriminadores son objetos de estudio
    (laptop/backpack/keyboard/book) para el aula, y de comida/bebida
    (dining table/cup/bottle/bowl) para la cafetería.
    """
    onto = get_ontology("http://cognitive-nav.org/venue.owl")

    with onto:
        # ------------------------------------------------------------------
        # Conceptos base
        # ------------------------------------------------------------------
        class Room(Thing):
            pass

        class PhysicalObject(Thing):
            pass

        class contains(ObjectProperty):
            domain = [Room]
            range = [PhysicalObject]

        # ------------------------------------------------------------------
        # Objetos (evidencia). Cada uno se corresponde con una clase YOLO/COCO
        # (ver LABEL_TO_ONTOLOGY en symbolic_node.py).
        # ------------------------------------------------------------------
        # Compartido (NO discrimina por sí solo)
        class Chair(PhysicalObject):        # YOLO: "chair"
            pass

        # Evidencia de aula (Classroom)
        class Laptop(PhysicalObject):       # YOLO: "laptop"
            pass

        class Backpack(PhysicalObject):     # YOLO: "backpack"
            pass

        class Keyboard(PhysicalObject):     # YOLO: "keyboard"
            pass

        class Book(PhysicalObject):         # YOLO: "book"
            pass

        class Screen(PhysicalObject):       # YOLO: "tv" (proyector / pantalla)
            pass

        # Evidencia de cafetería/comedor (Casino)
        class DiningTable(PhysicalObject):  # YOLO: "dining table"
            pass

        class Cup(PhysicalObject):          # YOLO: "cup"
            pass

        class Bottle(PhysicalObject):       # YOLO: "bottle"
            pass

        class Bowl(PhysicalObject):         # YOLO: "bowl"
            pass

        # ------------------------------------------------------------------
        # Zonas
        # ------------------------------------------------------------------
        class Casino(Room):
            pass

        class Classroom(Room):
            pass

        # ------------------------------------------------------------------
        # Reglas de clasificación (equivalent_to).
        # Cada alternativa exige >=2 objetos; "chair" solo se usa como
        # confirmador junto a un discriminador de aula.
        # ------------------------------------------------------------------
        Classroom.equivalent_to.append(
            Room & (
                (contains.some(Laptop) & contains.some(Chair)) |
                (contains.some(Laptop) & contains.some(Screen)) |
                (contains.some(Backpack) & contains.some(Chair)) |
                (contains.some(Keyboard) & contains.some(Chair)) |
                (contains.some(Book) & contains.some(Backpack))
            )
        )

        Casino.equivalent_to.append(
            Room & (
                (contains.some(DiningTable) & contains.some(Cup)) |
                (contains.some(DiningTable) & contains.some(Bottle)) |
                (contains.some(DiningTable) & contains.some(Bowl)) |
                (contains.some(Cup) & contains.some(Bottle)) |
                (contains.some(Bowl) & contains.some(Cup))
            )
        )

    return onto
