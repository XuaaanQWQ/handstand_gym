from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class Lite3JUMPCfg( LeggedRobotCfg ):
    class env:
        # change the observation dim
        frame_stack = 10 #action stack
        c_frame_stack = 3 #critic 网络的堆叠帧数
        num_single_obs = 45 #这个是传感器可以获得到的信息
        num_observations = int(frame_stack * num_single_obs) # 10帧正常的观测
        single_num_privileged_obs = 64  #不平衡的观测，包含了特权信息，正常传感器获得不到的信息
        num_privileged_obs = int(c_frame_stack * single_num_privileged_obs) # 3帧特权观测
        num_actions = 12
        num_envs = 8192 # number of environments
        episode_length_s = 5 # episode length in seconds
        env_spacing = 3.  # not used with heightfields/trimeshes 
        joint_num = 12
        send_timeouts=True

        reset_height = 0.13 # [m]
        reset_landing_error = 0.2 # [in m]

        debug_draw = False
        reset_orientation_error = 0.8 # [rad]

        jumping_target = True
        known_quaternion = True
        object_information = True

    class terrain:
        mesh_type = 'plane' # "heightfield" # none, plane, heightfield or trimesh
        horizontal_scale = 0.1 # [m]
        vertical_scale = 0.005 # [m]
        border_size = 25 # [m]
        curriculum = False
        static_friction = 0.6
        dynamic_friction = 0.6
        restitution = 0.
        # rough terrain only:
        measure_heights = False
        measured_points_x = [-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8] # 1mx1.6m rectangle (without center line)
        measured_points_y = [-0.5, -0.4, -0.3, -0.2, -0.1, 0., 0.1, 0.2, 0.3, 0.4, 0.5]
        selected = False# select a unique terrain type and pass all arguments
        terrain_kwargs = None # Dict of arguments for selected terrain
        max_init_terrain_level = 5 # starting curriculum state
        terrain_length = 8.
        terrain_width = 8.
        num_rows= 10 # number of terrain rows (levels)
        num_cols = 20 # number of terrain cols (types)
        # terrain types: [smooth slope, rough slope, stairs up, stairs down, discrete]
        terrain_proportions = [0., 0., 1.0, 0.0, 0.0]
        # trimesh only:
        slope_treshold = 0.75 # slopes above this threshold will be corrected to vertical surfaces
    class commands:
        curriculum = False
        max_curriculum = 0.8
        num_commands = 3 # default: lin_vel_x, lin_vel_y, ang_vel_yaw, heading (in heading mode ang_vel_yaw is recomputed from heading error)
        resampling_time = 5. # time before command are changed[s]
        heading_command = False # if true: compute ang vel command from heading error
        class ranges: 
            pos_dx_lim = [-0.0,0.8]
            pos_dy_lim = [-0.1,0.1]
            pos_dz_lim = [-0.0,0.8]
            # These are the steps for the jump distance changes every curriculum update.
            pos_variation_increment = [0.01,0.01,0.01]

    class init_state( LeggedRobotCfg.init_state ):
        pos = [0.0, 0.0, 0.4] # x,y,z [m]
        rot = [0.0, 0.0, 0.0, 1.0] # x,y,z,w [quat]
        lin_vel = [0.0, 0.0, 0.0]  # x,y,z [m/s]
        ang_vel = [0.0, 0.0, 0.0]  # x,y,z [rad/s]
        default_joint_angles = { # = target angles [rad] when action = 0.0

            'FL_HipX_joint': -0.1,   # [rad]
            'HL_HipX_joint': -0.1,   # [rad]
            'FR_HipX_joint': 0.1 ,  # [rad]
            'HR_HipX_joint': 0.1,   # [rad]

            'FL_HipY_joint': -0.8,     # [rad]
            'HL_HipY_joint': -1.0,#1.,   # [rad]
            'FR_HipY_joint': -0.8,     # [rad]
            'HR_HipY_joint': -1.0,#1.,   # [rad]

            'FL_Knee_joint': 1.5,   # [rad]
            'HL_Knee_joint': 1.5,    # [rad]
            'FR_Knee_joint': 1.5,  # [rad]
            'HR_Knee_joint': 1.5,    # [rad]
        }
        lie_joint_angles = { # = target angles [rad] when action = 0.0

            'FL_HipX_joint': 0.,   # [rad]
            'HL_HipX_joint': 0.,   # [rad]
            'FR_HipX_joint': -0. ,  # [rad]
            'HR_HipX_joint': -0.,   # [rad]

            'FL_HipY_joint': -1.25,     # [rad]
            'HL_HipY_joint': -1.25,#1.,   # [rad]
            'FR_HipY_joint': -1.25,     # [rad]
            'HR_HipY_joint': -1.25,#1.,   # [rad]

            'FL_Knee_joint': 2.,   # [rad]
            'HL_Knee_joint': 2.,    # [rad]
            'FR_Knee_joint': 2.,  # [rad]
            'HR_Knee_joint': 2.,    # [rad]
        }
    class control( LeggedRobotCfg.control ):
        # PD Drive parameters:
        control_type = 'P'
        stiffness = {'joint': 40.}  # [N*m/rad]
        damping = {'joint': 1}     # [N*m*s/rad]
        # action scale: target angle = actionScale * action + defaultAngle
        action_scale = 0.25
        # decimation: Number of control action updates @ sim DT per policy DT
        decimation = 4
    class asset:
        file = '{LEGGED_GYM_ROOT_DIR}/resources/robots/Lite3/urdf/Lite3.urdf'
        name = "lite3_jump"
        foot_name = "FOOT"
        penalize_contacts_on = ["THIGH", "SHANK"]
        terminate_after_contacts_on = ["TORSO"]
        target_gravity=[0,0,-1]
        self_collisions = 0 # 1 to disable, 0 to enable...bitwise filter
        disable_gravity = False
        collapse_fixed_joints = False # merge bodies connected by fixed joints. Specific fixed joints can be kept by adding " <... dont_collapse="true">
        fix_base_link = False # fixe the base of the robot
        default_dof_drive_mode = 3 # see GymDofDriveModeFlags (0 is none, 1 is pos tgt, 2 is vel tgt, 3 effort)
        self_collisions = 0 # 1 to disable, 0 to enable...bitwise filter
        replace_cylinder_with_capsule = True # replace collision cylinders with capsules, leads to faster/more stable simulation
        flip_visual_attachments = True # Some .obj meshes must be flipped from y-up to z-up
        
        density = 0.001
        angular_damping = 0.
        linear_damping = 0.
        max_angular_velocity = 1000.
        max_linear_velocity = 1000.
        armature = 0.
        thickness = 0.01
    class domain_rand:
        randomize_friction = True
        friction_range = [0.4,0.8]

        push_robots = True
        push_interval_s = 4
        max_push_vel_xy = 0.4
        max_push_ang_vel = 0.6

        randomize_base_mass = True
        added_base_mass_range = [-1,1]

        randomize_link_mass = True
        multiplied_link_mass_range = [0.9, 1.1]

        randomize_base_com = True
        added_base_com_range = [-0.02, 0.02]

        randomize_pd_gains = True
        stiffness_multiplier_range = [0.9, 1.1]  
        damping_multiplier_range = [0.1, 1.1]    


        randomize_motor_zero_offset = True
        motor_zero_offset_range = [-0.035, 0.035] # Offset to add to the motor angles

        add_obs_latency = True # no latency for obs_action
        randomize_obs_motor_latency = True
        randomize_obs_imu_latency = True
        range_obs_motor_latency = [1, 3]
        range_obs_imu_latency = [1, 3]
        
        add_cmd_action_latency = True
        randomize_cmd_action_latency = True
        range_cmd_action_latency = [1, 3]

    class rewards:
        class scales:
            before_setting=0.6
            post_landing_pos=5.0
            post_landing_ori=5.0
            line_z=6.0
            base_height_flight=4.0
            base_height_stance=2.0
            orientation=0.3
            default_pose_air=-0.2
            ang_vel_xy=0.2
            recovery=4.
            torques=-0.0001
            dof_pos_limits=-1.
            dof_vel_limits=-1.
            torque_limits=-1.
            termination=0.0
            collision=-1.
            action_rate=-0.005
            action_rate_second_order=-0.0001
            feet_contact_forces=-0.2

        max_contact_force=165
        only_positive_rewards=False
        reward_sigma=0.25
        target_height=0.6
    class normalization:
        class obs_scales:
            lin_vel = 2.0
            ang_vel = 0.25
            dof_pos = 1.0
            dof_vel = 0.05
            height_measurements = 5.0
            quat = 1.
        clip_observations = 100.
        clip_actions = 100.

    class noise:
        add_noise = True
        noise_level = 1.0 # scales other values
        class noise_scales:
            dof_pos = 0.01
            dof_vel = 1.5
            lin_vel = 0.1
            ang_vel = 0.2
            gravity = 0.05
            quat = 0.1
            height_measurements = 0.1

    # viewer camera:
    class viewer:
        ref_env = 0
        pos = [10, 0, 6]  # [m]
        lookat = [11., 5, 3.]  # [m]

    class sim:
        dt =  0.005
        substeps = 1
        gravity = [0., 0. ,-9.81]  # [m/s^2]
        up_axis = 1  # 0 is y, 1 is z

        class physx:
            num_threads = 10
            solver_type = 1  # 0: pgs, 1: tgs
            num_position_iterations = 4
            num_velocity_iterations = 0
            contact_offset = 0.01  # [m]
            rest_offset = 0.0   # [m]
            bounce_threshold_velocity = 0.5 #0.5 [m/s]
            max_depenetration_velocity = 1.0
            max_gpu_contact_pairs = 2**23 #2**24 -> needed for 8000 envs and more
            default_buffer_size_multiplier = 5
            contact_collection = 2 # 0: never, 1: last sub-step, 2: all sub-steps (default=2)


class Lite3JUMPPPO(LeggedRobotCfgPPO):
    seed = 1
    runner_class_name = 'OnPolicyRunner'
    class policy:
        init_noise_std = 1.0
        actor_hidden_dims = [512, 256, 128]
        critic_hidden_dims = [512, 256, 128]
        activation = 'elu' # can be elu, relu, selu, crelu, lrelu, tanh, sigmoid

    class algorithm:
        # training params
        value_loss_coef = 1.0
        use_clipped_value_loss = True
        clip_param = 0.2
        entropy_coef = 0.01
        num_learning_epochs = 5
        num_mini_batches = 4 # mini batch size = num_envs*nsteps / nminibatches
        learning_rate = 1.e-5 #5.e-4
        schedule = 'adaptive' # could be adaptive, fixed
        gamma = 0.99
        lam = 0.95
        desired_kl = 0.01
        max_grad_norm = 1.
        sym_loss = True
        obs_permutation = [0.0001, -1, 2, 
                           -3,4,-5,-6,7,-8,
                       -12,13,14,-9,10,11,-18,19,20,-15,16,17,
                       -24,25,26,-21,22,23,-30,31,32,-27,28,29,
                       -36,37,38,-33,34,35,-42,43,44,-39,40,41]
        act_permutation = [ -3, 4, 5, -0.0001, 1, 2, -9, 10, 11,-6, 7, 8,]#关节电机的对陈关系
        frame_stack = 10
        sym_coef = 1.0
    class runner:
        policy_class_name = 'ActorCritic'
        algorithm_class_name = 'PPO'
        num_steps_per_env = 24 # per iteration
        max_iterations = 6000 # number of policy updates

        # logging
        save_interval = 500 # check for potential saves every this many iterations
        experiment_name = 'lite3_spring_jump'
        run_name = ''
        # load and resume
        resume = False
        load_run = -1 # -1 = last run
        checkpoint = -1 # -1 = last saved model
        resume_path = None # updated from load_run and chkpt