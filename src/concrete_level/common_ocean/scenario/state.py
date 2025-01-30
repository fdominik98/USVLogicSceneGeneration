__author__ = "Bruno Maione"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2023a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "development"

from commonroad.common.util import Interval, AngleInterval
from commonroad.geometry.shape import Shape
from commonroad.scenario.state import State
from dataclasses import dataclass
from typing import Any, Union
import numpy as np

FloatExactOrInterval = Union[float, Interval]
AngleExactOrInterval = Union[float, AngleInterval]
ExactOrShape = Union[np.ndarray, Shape]

class GeneralState(State):
    """
    This is a class representing the custom state. State variables can be added at runtime. The attributes position
    and orientation/velocity_y are necessary for successful file reading.
    """

    def __init__(self, **attributes):
        """
        Additional constructor for CustomState class.

        :param attributes: Variable number of attributes each consisting of name and value.
        """
        if len(attributes) > 0:  # if one wants to use the attribute adding methods manually
            super().__init__(attributes["time_step"])
        for name, value in attributes.items():
            if name == "time_step":
                continue
            self.add_attribute(name)
            self.set_value(name, value)

    def add_attribute(self, new_attr: str):
        """
        Adds a new attribute to custom state.

        :param new_attr: Attribute name
        """
        setattr(self, new_attr, None)

    def set_value(self, attr: str, value: Any):
        """
        Sets value to attribute.

        :param attr: Attribute name
        :param value: Value
        """
        assert attr in self.attributes, "{} is not an attribute of this custom state!".format(attr)

        setattr(self, attr, value)

@dataclass(eq=False)
class PMState(State):
    """
    This is a class representing Point Mass State (PM State).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param velocity: Velocity :math:`v_x` in longitudinal direction
    :param velocity_y: Velocity :math:`v_x` in lateral direction
    """
    position: ExactOrShape = None
    velocity: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None

@dataclass(eq=False)
class VPState(State):
    """
    This is a class representing Velocity-Constrained Point Mass State (VP State).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param velocity: Velocity :math:`v_x` in longitudinal direction
    :param velocity_y: Velocity :math:`v_x` in lateral direction
    """
    position: ExactOrShape = None
    velocity: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None

@dataclass(eq=False)
class YPState(State):
    """
    This is a class representing Yaw-Constrained Point Mass State (VP State).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param orientation: Yaw angle :math:`\\Psi`
    :param velocity: Velocity :math:`n` aligned with the orientation of the vessel (also called surge)
    """
    position: ExactOrShape = None
    orientation: AngleExactOrInterval = None
    velocity: FloatExactOrInterval = None

@dataclass(eq=False)
class TFState(State):
    """
    This is a class representing Three Degrees of Freedom Model (3F State).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param orientation: Yaw angle :math:`\\Psi`
    :param velocity: Velocity :math:`n` aligned with the orientation of the vessel (also called surge)
    :param velocity_y: Velocity :math:`v` lateral to the orientation of the vessel (also called sway)
    :paran yaw_rate: Yaw rate :math:`\\omega`
    """
    position: ExactOrShape = None
    orientation: AngleExactOrInterval = None
    velocity: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None
    yaw_rate: FloatExactOrInterval = None

@dataclass(eq=False)
class VesselState(State):
    """
    This is a class representing an arbitrary vesel state with all possible state elements (slots),
    which comprise the necessary tate element to describe the tates of all CommonOcean vessel models.

    :param position: :math:`s_x`- and :math:`s_y`-position in a global
    coordinate system. Exact positions
        are given as numpy array [x, y], uncertain positions are given as :class:`commonroad.geometry.shape.Shape`
    :param orientation: yaw angle :math:`\Psi`. Exact values are given as real number, uncertain values are given as
        :class:`commonroad.common.util.AngleInterval`
    :param velocity: velocity :math:`v_x` in longitudinal direction in the vessel-fixed coordinate system. Exact
        values are given as real number, uncertain values are given as :class:`commonroad.common.util.Interval`
    :param rudder_angle: rudder angle :math:`\beta`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param rudder_angle_speed: rudder angle speed :math:`\dot{\beta}` Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param yaw_rate: yaw rate :math:`\dot{\Psi}`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param roll_angle: roll angle :math:`\Phi_S`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param roll_rate: roll rate :math:`\dot{\Phi}_S`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param pitch_angle: pitch angle :math:`\Theta_S`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param pitch_rate: pitch rate :math:`\dot{\Theta}_S`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param velocity_y: velocity :math:`v_y` in lateral direction in the vessel-fixed coordinate system. Exact
        values are given as real number, uncertain values are given as :class:`commonroad.common.util.Interval`
    :param position_z: position :math:`s_z` (height) from ground. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param velocity_z: velocity :math:`v_z` in vertical direction perpendicular to road plane. Exact values are
        given as real number, uncertain values are given as :class:`commonroad.common.util.Interval`
    :param roll_angle_front: roll angle front :math:`\Phi_{UF}`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param roll_rate_front: roll rate front :math:`\dot{\Phi}_{UF}`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param velocity_y_front: velocity :math:`v_{y,UF}` in y-direction front. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param position_z_front: position :math:`s_{z,UF}` in z-direction front. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param velocity_z_front: velocity :math:`v_{z,UF}` in z-direction front. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param roll_angle_rear: roll angle rear :math:`\Phi_{UR}`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param roll_rate_rear: roll rate rear :math:`\dot{\Phi}_{UR}`. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param velocity_y_rear: velocity :math:`v_{y,UR}` in y-direction rear. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param position_z_rear: position :math:`s_{z,UR}` in z-direction rear. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param velocity_z_rear: velocity :math:`v_{z,UR}` in z-direction rear. Exact values are given as real number,
        uncertain values are given as :class:`commonroad.common.util.Interval`
    :param acceleration: acceleration :math:`a_x`. We optionally include acceleration as a state variable for
        obstacles to provide additional information, e.g., for motion prediction, even though acceleration is often
        used as an input for vessel models. Exact values are given as real number, uncertain values are given as
        :class:`commonroad.common.util.Interval`
    :param acceleration_y: velocity :math:`a_y`.
        We optionally include acceleration as a state variable for obstacles to provide additional information,
        e.g., for motion prediction, even though acceleration is often used as an input for vessel models. Exact
        values are given as real number, uncertain values are given as :class:`commonroad.common.util.Interval`
    :param jerk: acceleration :math:`j`. We optionally include jerk as a state variable for
        obstacles to provide additional information, e.g., for motion prediction, even though jerk is often
        used as an input for vessel models. Exact values are given as real number, uncertain values are given as
        :class:`commonroad.common.util.Interval`
    :param force_orientation: force :math:`F_x`. We optionally include the body-fixed force aligned with orientation
        as a state variable to provide additional information to vessel dynamics inputs, e.g., for motion prediction.
        Exact values are given as real number, uncertain values are given as :class:`commonroad.common.util.Interval`
    :param force_lateral: force :math:`F_y`. We optionally include the body-fixed force lateral to orientation
        as a state variable to provide additional information to vessel dynamics inputs, e.g., for motion prediction.
        Exact values are given as real number, uncertain values are given as :class:`commonroad.common.util.Interval`
    :param yaw_moment: force :math:`M_{\Phi}`. We optionally include the yaw_momment as a state variable to provide additional
        information to vessel dynamics inputs, e.g., for motion prediction. Exact values are given as real number, uncertain
        values are given as :class:`commonroad.common.util.Interval`
    """
    position: ExactOrShape = None
    orientation: AngleExactOrInterval = None
    velocity: FloatExactOrInterval = None
    rudder_angle: AngleExactOrInterval = None
    rudder_angle_speed: FloatExactOrInterval = None
    yaw_rate: FloatExactOrInterval = None
    roll_angle: AngleExactOrInterval = None
    roll_rate: FloatExactOrInterval = None
    pitch_angle: AngleExactOrInterval = None
    pitch_rate: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None
    position_z: FloatExactOrInterval = None
    velocity_z: FloatExactOrInterval = None
    roll_angle_front: AngleExactOrInterval = None
    roll_rate_front: FloatExactOrInterval = None
    velocity_y_front: FloatExactOrInterval = None
    position_z_front: FloatExactOrInterval = None
    velocity_z_front: FloatExactOrInterval = None
    roll_angle_rear: AngleExactOrInterval = None
    roll_rate_rear: FloatExactOrInterval = None
    velocity_y_rear: FloatExactOrInterval = None
    position_z_rear: FloatExactOrInterval = None
    velocity_z_rear: FloatExactOrInterval = None
    acceleration: FloatExactOrInterval = None
    acceleration_y: FloatExactOrInterval = None
    jerk: FloatExactOrInterval = None
    force_orientation: FloatExactOrInterval = None
    force_lateral: FloatExactOrInterval = None
    yaw_moment: FloatExactOrInterval = None
