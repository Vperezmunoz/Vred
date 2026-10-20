# Steering Wheel Constraint Example
# source: steering-wheel.html

# Removes all constraints

  constraints = vrConstraintService.getConstraints()

  if constraints:
      for i in constraints:
          print(f'Removing Constraint: {i}')
          targets = i.getTargetNodes()

          for j in targets:
              print(j.getName())

          vrConstraintService.deleteConstraint(i)
  else:
      print('No Constraints found.')

  del wheel_timer

  # Set up constraints for the wheels and register a function that moves
  # the targe nodes when the steering wheel has been manually rotated.

  # Store last steering wheel rotation value
  last_wheel_rotation = 0.0

  # Fetch the required nodes from the scene graph
  wheel_group = vrNodeService.findNode('Front Wheels')
  wheel_left = vrNodeService.findNode('Wheel-Left')
  wheel_right = vrNodeService.findNode('Wheel-Right')

  wheel_target_group = vrNodeService.findNode('Wheel Targets')
  wheel_left_target = vrNodeService.findNode('Target-Left')
  wheel_right_target = vrNodeService.findNode('Target-Right')

  # Next create two aim constraints for the wheels. We use the two green spheres
  # as targets for the wheel_left and wheel_right nodes. That means the wheel nodes will
  # now rotate automatically to face the position of their target node as long as the
  # aim constraint is active.
  lf_constraint = vrConstraintService.createAimConstraint([wheel_left_target], [], wheel_left)
  rf_constraint = vrConstraintService.createAimConstraint([wheel_right_target], [], wheel_right)

  steering_wheel = vrNodeService.findNode('Steering Wheel')

  # This function checks the steering wheel for manual rotation around the x axis.
  # For that it is connected to a vrTimer object which calls this function once every frame.
  # When the wheel is rotated, it translates the wheel targets along the y axis,
  # causing the wheels to change their rotation because of the aim constraints.
  def check_steering_wheel_angle():
      global last_wheel_rotation

      current_rot = round(steering_wheel.getRotationAsEuler().x(), 2)

      if current_rot != last_wheel_rotation: # Don't move when steering wheel stops rotating

          # Lock wheel at maximum rotation angle
          if current_rot <= -540:
              steering_wheel.setRotationAsEuler(QVector3D(-540, steering_wheel.getRotationAsEuler().y(), steering_wheel.getRotationAsEuler().z()))
          elif current_rot >= 540:
              steering_wheel.setRotationAsEuler(QVector3D(540, steering_wheel.getRotationAsEuler().y(), steering_wheel.getRotationAsEuler().z()))

          else:
              print(f'Current rotation: {current_rot} / {last_wheel_rotation}')

              delta = abs(round(current_rot - last_wheel_rotation, 2))
              print(f'Delta: {delta}')

              if current_rot > last_wheel_rotation:
                  wheel_target_group.setTranslation(QVector3D(
                      wheel_target_group.getTranslation().x(),
                      wheel_target_group.getTranslation().y() - delta,
                      wheel_target_group.getTranslation().z())
                      )
              if current_rot < last_wheel_rotation:
                  wheel_target_group.setTranslation(QVector3D(
                      wheel_target_group.getTranslation().x(),
                      wheel_target_group.getTranslation().y() + delta,
                      wheel_target_group.getTranslation().z())
                      )

          last_wheel_rotation = round(steering_wheel.getRotationAsEuler().x(), 2)

  wheel_timer = vrTimer()
  wheel_timer.connect(check_steering_wheel_angle)
  wheel_timer.setActive(True)

  print("Wheels constrained to targets.")

  # This variant turns the steering wheel to the left.
  # For that it interpolates the x euler angle between the current
  # wheel rotation and 360 with a 3 second duration.

  time_in_seconds = 3.0
  wheel_turn_left = vrInterpolator(True)

  wheel_rot_left = vrRotationSlide(steering_wheel,
      steering_wheel.getRotationAsEuler().x(),
      steering_wheel.getRotationAsEuler().y(),
      steering_wheel.getRotationAsEuler().z(),
      360,
      steering_wheel.getRotationAsEuler().y(),
      steering_wheel.getRotationAsEuler().z(),
      time_in_seconds)

  wheel_turn_left.add(wheel_rot_left)
  wheel_turn_left.setActive(True)

  # This variant turns the steering wheel back to the center.
  # It interpolates the x euler angle between the current
  # wheel rotation and 0 with a 3 second duration.

  time_in_seconds = 3.0
  wheel_return = vrInterpolator(True)

  # The first three angles are the starting position, the following
  # three angles are the target position of the rotation

  wheel_rot = vrRotationSlide(steering_wheel,
      steering_wheel.getRotationAsEuler().x(),
      steering_wheel.getRotationAsEuler().y(),
      steering_wheel.getRotationAsEuler().z(),
      0,
      steering_wheel.getRotationAsEuler().y(),
      steering_wheel.getRotationAsEuler().z(),
      time_in_seconds)

  def align_wheels():
      # Re-align front wheels
      wheel_target_group.setTranslation(QVector3D(wheel_target_group.getTranslation().x(), 0.0, wheel_target_group.getTranslation().z()))

  wheel_return.add(wheel_rot)
  wheel_return.connect(align_wheels)
  wheel_return.setActive(True)

  # This variant turns the steering wheel to the right.
  # For that it interpolates the x euler angle between the current
  # wheel rotation and -360 with a 3 second duration.

  time_in_seconds = 3.0
  wheel_turn_right = vrInterpolator(True)

  wheel_rot_right = vrRotationSlide(steering_wheel,
      steering_wheel.getRotationAsEuler().x(),
      steering_wheel.getRotationAsEuler().y(),
      steering_wheel.getRotationAsEuler().z(),
      -360,
      steering_wheel.getRotationAsEuler().y(),
      steering_wheel.getRotationAsEuler().z(),
      time_in_seconds)

  wheel_turn_right.add(wheel_rot_right)
  wheel_turn_right.setActive(True)
