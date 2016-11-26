#!/usr/bin/env python3

import speech_recognition as sr
import asyncio
import cozmo

###### ACTIONS ######
def do_blocks(robot):
	print("looking for my blocks...")
	lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

	cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=40)

	print("found %s cube(s)" % cubes)

	lookaround.stop()

	if len(cubes) == 0:
		robot.play_anim_trigger(cozmo.anim.Triggers.MajorFail).wait_for_completed()
	elif len(cubes) == 1:
		robot.run_timed_behavior(cozmo.behavior.BehaviorTypes.RollBlock, active_time=60)
	else:
		robot.run_timed_behavior(cozmo.behavior.BehaviorTypes.StackBlocks, active_time=60)

def do_square():
	print("dancing...")
def do_lookforface(robot):
	any_face = None
	print("Looking for a face...")
	robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
	robot.move_lift(-3)
	look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)

	try:
		any_face = robot.world.wait_for_observed_face(timeout=30)

	except asyncio.TimeoutError:
		print("Didn't find anyone :-(")

	finally:
		# whether we find it or not, we want to stop the behavior
		look_around.stop()

	if any_face is None:
		robot.play_anim_trigger(cozmo.anim.Triggers.MajorFail).wait_for_completed()
		return

	print("Yay, found someone!")

	anim = robot.play_anim_trigger(cozmo.anim.Triggers.LookInPlaceForFacesBodyPause)
	anim.wait_for_completed()

def do_followface(robot):
	print("Following your face - any face...")
	# Move lift down and tilt the head up
	robot.move_lift(-3)
	robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

	face_to_follow = None

	while True:
		turn_action = None
		if face_to_follow:
		# start turning towards the face
			turn_action = robot.turn_towards_face(face_to_follow)

		if not (face_to_follow and face_to_follow.is_visible):
			# find a visible face, timeout if nothing found after a short while
			try:
				face_to_follow = robot.world.wait_for_observed_face(timeout=30)
			except asyncio.TimeoutError:
				print("Didn't find a face - exiting!")
				return

		if turn_action:
			# Complete the turn action if one was in progress
			turn_action.wait_for_completed()

		#time.sleep(.1)

def do_say(recognized, robot):
	line = recognized.split(' ', 2)[2]
	robot.say_text(line).wait_for_completed()
	print("Cozmo said: %s" % line)

def do_takepicture(robot):
	print("taking a picture...")
	pic_filename = "picture.png"
	robot.say_text("Say cheese!").wait_for_completed()
	latest_image = robot.world.latest_image
	latest_image.raw_image.convert('L').save(pic_filename)
	print("picture saved as: " + pic_filename)


###### COMMANDS ######
command_activate = "Cosmo"
command_say = "say"
command_dance = "dance"
command_pickup = "pick up"
command_takepicture = "take a picture"
command_takepictureofme = "take a picture of me"
command_lookatme = "look at me"
command_followme = "follow me"

def hear(source, r, robot):
	audio = r.listen(source)
	try:
		recognized = r.recognize_google(audio)
		print("You said: " + recognized)
		if command_activate in recognized or command_activate.lower() in recognized:
			print("Action command recognized")

			if command_pickup in recognized:
				do_blocks(robot)

			elif command_dance in recognized:
				do_dance()

			elif command_lookatme in recognized:
				do_lookforface(robot)

			elif command_followme in recognized:
				do_lookforface(robot)
				do_followface(robot)

			elif command_takepictureofme in recognized:
				do_lookforface(robot)
				do_takepicture(robot)

			elif command_takepicture in recognized:
				do_takepicture(robot)

			elif command_say in recognized:
				do_say(recognized, robot)

			else:
				print("Command not recognized")

		else:
			print("You did not say the magic word " + command_activate)

	except sr.UnknownValueError:
		print("Google Speech Recognition could not understand audio")
	except sr.RequestError as e:
		print("Could not request results from Google Speech Recognition service; {0}".format(e))


def run(sdk_conn):
    '''The run method runs once the Cozmo SDK is connected.'''
    robot = sdk_conn.wait_for_robot()
    try:
        print("Say something")
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while 1:
                hear(source, r, robot)
                print("say something else")
                recognized = None

    except KeyboardInterrupt:
        print("")
        print("Exit requested by user")


if __name__ == "__main__":
	cozmo.setup_basic_logging()
	try:
		cozmo.connect_with_tkviewer(run, force_on_top=True)
	except cozmo.ConnectionError as e:
		sys.exit("A connection error occurred: %s" % e)
