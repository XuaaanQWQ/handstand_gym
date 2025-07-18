import time
from isaacgym.torch_utils import *
import mujoco.viewer
import mujoco
import numpy as np
from legged_gym import LEGGED_GYM_ROOT_DIR
import torch
import yaml


def get_gravity_orientation(quaternion):
    qw = quaternion[0]
    qx = quaternion[1]
    qy = quaternion[2]
    qz = quaternion[3]

    gravity_orientation = np.zeros(3)

    gravity_orientation[0] = 2 * (-qz * qx + qw * qy)
    gravity_orientation[1] = -2 * (qz * qy + qw * qx)
    gravity_orientation[2] = 1 - 2 * (qw * qw + qz * qz)

    return gravity_orientation


def pd_control(target_q, q, kp, target_dq, dq, kd):
    """Calculates torques from position commands"""
    return (target_q - q) * kp + (target_dq - dq) * kd 
from pynput import keyboard

def key_callback(key):
    try:
        print(key.char)
        if key.char == '6':
            cmd[0] += 0.5
        elif key.char == '7':
            cmd[0]  -= 0.5
        elif key.char == '8':
            cmd[1]  += 0.5
        elif key.char == '9':
            cmd[1]  -= 0.5
        elif key.char == '-':
            cmd[2]  += 0.5
        elif key.char == '=':
            cmd[2]  -= 0.5
        elif key.char == '1':
            cmd[0]=0
            cmd[1]=0
            cmd[2]=0

    except AttributeError:
        pass
listener = keyboard.Listener(on_press=key_callback)
listener.start()
if __name__ == "__main__":
    # get config file name from command line
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="config file name in the config folder")
    args = parser.parse_args()
    config_file = args.config_file
    with open(f"{LEGGED_GYM_ROOT_DIR}/deploy/deploy_mujoco/configs/{config_file}", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        policy_path = config["policy_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)
        xml_path = config["xml_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)

        simulation_duration = config["simulation_duration"]
        simulation_dt = config["simulation_dt"]
        control_decimation = config["control_decimation"]

        kps = np.array(config["kps"], dtype=np.float32)
        kds = np.array(config["kds"], dtype=np.float32)

        default_angles = np.array(config["default_angles"], dtype=np.float32)

        ang_vel_scale = config["ang_vel_scale"]
        dof_pos_scale = config["dof_pos_scale"]
        dof_vel_scale = config["dof_vel_scale"]
        lin_vel_scale = config["lin_vel_scale"]
        action_scale = config["action_scale"]
        cmd_scale = np.array(config["cmd_scale"], dtype=np.float32)

        num_actions = config["num_actions"]
        num_obs = config["num_obs"]
        
        cmd = np.array(config["cmd_init"], dtype=np.float32)

    # define context variables
    action = np.zeros(num_actions, dtype=np.float32)
    target_dof_pos = default_angles.copy()
    obs = np.zeros(num_obs, dtype=np.float32)

    counter = 0

    # Load robot model
    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)
    m.opt.timestep = simulation_dt

    # load policy
    policy = torch.jit.load(policy_path)

    with mujoco.viewer.launch_passive(m, d,key_callback=key_callback) as viewer:
        # Close the viewer automatically after simulation_duration wall-seconds.
        start = time.time()
        while viewer.is_running() and (time.time() - start < 1000000) :
            step_start = time.time()
            if  (time.time() - start>3):
                tau = pd_control(target_dof_pos, d.qpos[7:], kps, np.zeros_like(kds), d.qvel[6:], kds)
                d.ctrl[:] = tau
            # mj_step can be replaced with code that also evalua
            # a policy and applies a control signal before stepping the physics.
            mujoco.mj_step(m, d)

            counter += 1
            if counter % control_decimation == 0:
                # Apply control signal here.

                # create observation
                qj = d.qpos[7:]
                dqj = d.qvel[6:]
                quat = d.qpos[3:7]
                omega = d.qvel[3:6]
                # linevel=d.qvel[0:3]
                qj = (qj - default_angles) * dof_pos_scale
                dqj = dqj * dof_vel_scale
                gravity_orientation = get_gravity_orientation(quat)
                omega = omega * ang_vel_scale
                # linevel=lin_vel_scale*linevel
                period = 0.8
                count = counter * simulation_dt
                phase = count % period / period













                # 原始代码
                quat_tensor = torch.from_numpy(quat[[1,2,3,0]])  # shape=[4]
                vel_tensor = torch.from_numpy(d.qvel[0:3])       # shape=[3]

                # 修改后（添加unsqueeze(0)）
                linevel = quat_rotate_inverse(
                    quat_tensor.unsqueeze(0),  # shape变为[1,4]
                    vel_tensor.unsqueeze(0)    # shape变为[1,3]
                ) * lin_vel_scale

                # 如果结果需要去掉batch维度
                linevel = linevel.squeeze(0)


                obs[:3] = linevel
                obs[3:6] = omega
                obs[6:9] = gravity_orientation
                obs[9 : 12] = cmd * cmd_scale
                obs[12:24] = qj
                obs[24:36] = dqj
                obs[36:48] = action
                print(gravity_orientation)
                obs_tensor = torch.from_numpy(obs).unsqueeze(0)
                # policy inference
                action = policy(obs_tensor).detach().numpy().squeeze()
                # transform action to target_dof_pos
                target_dof_pos = action * action_scale + default_angles
                with open("/home/zju/YuSongmin/RL_Leggedgym/unitree_rl_gym-main/deploy/deploy_mujoco/simulation_data.txt", "a+") as file:
                    file.write(str(omega[0])+","+str(omega[1])+","+str(omega[2])+"\n")
            # Pick up changes to the physics state, apply perturbations, update options from GUI.
            viewer.sync()

            # Rudimentary time keeping, will drift relative to wall clock.
            time_until_next_step = m.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)
