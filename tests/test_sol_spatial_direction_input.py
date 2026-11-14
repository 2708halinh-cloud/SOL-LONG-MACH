"""SpatialDirectionInput regression: orientation != binary authorization."""
import unittest
from runtime.sol_spatial_direction_input import (
    DIRECTIONS, SpatialContextError, parse_spatial_input
)


class SpatialDirectionTests(unittest.TestCase):
    def test_eight_vectors_match_eight_bearings(self):
        self.assertEqual(len(DIRECTIONS), 8)
        for code, spec in DIRECTIONS.items():
            out = parse_spatial_input(spec["vector"])
            self.assertEqual(out["payload"]["direction_code"], code)
            self.assertEqual(out["payload"]["angle"], spec["angles"][0])
            self.assertIsNone(out["permission_decision"])
            self.assertFalse(out["downstream_execution_performed"])

    def test_north_360_alias(self):
        out = parse_spatial_input({
            "agent_id": "SOL_YIN", "input_type": "spatial_vector",
            "payload": {"direction_code": "N", "angle": 360, "label_vi": "Bắc"}})
        self.assertEqual(out["payload"]["angle"], 360)

    def test_source_example_ne(self):
        out = parse_spatial_input('{"agent_id":"SOL_YIN","input_type":"spatial_vector","payload":{"direction_code":"NE","label_vi":"Đông Bắc","angle":45}}')
        self.assertEqual(out["payload"]["vector"], [1, 1])

    def test_names_are_directions(self):
        self.assertEqual(parse_spatial_input("Tây Bắc")["payload"]["direction_code"], "NW")
        self.assertEqual(parse_spatial_input("south-east")["payload"]["direction_code"], "SE")

    def test_true_false_are_not_direction(self):
        for value in [True, False, {"allowed": True}, {"forbidden": False}]:
            with self.subTest(value=value), self.assertRaises(SpatialContextError):
                parse_spatial_input(value)

    def test_code_angle_mismatch(self):
        with self.assertRaisesRegex(SpatialContextError, "ANGLE"):
            parse_spatial_input({"agent_id": "S", "input_type": "spatial_vector",
                                 "payload": {"direction_code": "N", "angle": 90}})

    def test_label_mismatch(self):
        with self.assertRaisesRegex(SpatialContextError, "LABEL"):
            parse_spatial_input({"agent_id": "S", "input_type": "spatial_vector",
                                 "payload": {"direction_code": "E", "angle": 90, "label_vi": "Bắc"}})

    def test_blank_agent_id_and_missing_payload(self):
        with self.assertRaises(SpatialContextError):
            parse_spatial_input({"agent_id": "", "input_type": "spatial_vector", "payload": {}})
        with self.assertRaises(SpatialContextError):
            parse_spatial_input({"agent_id": "SOL", "input_type": "spatial_vector"})

    def test_invalid_vector_is_not_silent_success(self):
        with self.assertRaises(SpatialContextError):
            parse_spatial_input([3, 4])

    def test_boolean_coordinates_do_not_pass(self):
        with self.assertRaises(SpatialContextError):
            parse_spatial_input([True, 1])


if __name__ == "__main__":
    unittest.main()
