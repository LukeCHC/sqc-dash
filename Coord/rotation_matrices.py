import numpy as np
import numpy as np

def R1(thetas):
    """Rotation matrices for rotations around the x-axis by angles in thetas."""
    c, s = np.cos(thetas), np.sin(thetas)
    return np.array([
        [np.ones_like(thetas), np.zeros_like(thetas), np.zeros_like(thetas)],
        [np.zeros_like(thetas), c, s],
        [np.zeros_like(thetas), -s, c]
    ]).transpose(2, 0, 1)

def R2(thetas):
    """Rotation matrices for rotations around the y-axis by angles in thetas."""
    c, s = np.cos(thetas), np.sin(thetas)
    return np.array([
        [c, np.zeros_like(thetas), -s],
        [np.zeros_like(thetas), np.ones_like(thetas), np.zeros_like(thetas)],
        [s, np.zeros_like(thetas), c]
    ]).transpose(2, 0, 1)

def R3(thetas):
    """Rotation matrices for rotations around the z-axis by angles in thetas."""
    c, s = np.cos(thetas), np.sin(thetas)
    return np.array([
        [c, s, np.zeros_like(thetas)],
        [-s, c, np.zeros_like(thetas)],
        [np.zeros_like(thetas), np.zeros_like(thetas), np.ones_like(thetas)]
    ]).transpose(2, 0, 1)

# def R1(thetas):
#     """Rotation matrices for rotations around the x-axis by angles in thetas."""
#     c, s = np.cos(thetas), np.sin(thetas)
#     return np.array([
#         [np.ones_like(thetas), np.zeros_like(thetas), np.zeros_like(thetas)],
#         [np.zeros_like(thetas), c, -s],
#         [np.zeros_like(thetas), s, c]
#     ]).transpose(2, 0, 1)

# def R2(thetas):
#     """Rotation matrices for rotations around the y-axis by angles in thetas."""
#     c, s = np.cos(thetas), np.sin(thetas)
#     return np.array([
#         [c, np.zeros_like(thetas), s],
#         [np.zeros_like(thetas), np.ones_like(thetas), np.zeros_like(thetas)],
#         [-s, np.zeros_like(thetas), c]
#     ]).transpose(2, 0, 1)

# def R3(thetas):
#     """Rotation matrices for rotations around the z-axis by angles in thetas."""
#     c, s = np.cos(thetas), np.sin(thetas)
#     return np.array([
#         [c, -s, np.zeros_like(thetas)],
#         [s, c, np.zeros_like(thetas)],
#         [np.zeros_like(thetas), np.zeros_like(thetas), np.ones_like(thetas)]
#     ]).transpose(2, 0, 1)

if __name__ == "__main__":
    # Example usage with an array of angles:
    thetas = np.radians([45, 90, 135])  # Convert degrees to radians
    
    rot_x = R1(thetas)
    rot_y = R2(thetas)
    rot_z = R3(thetas)

    for i, theta in enumerate(thetas):
        print(f"Rotation matrix around the x-axis for angle {np.degrees(theta)} degrees:\n", rot_x[i])
        print(f"Rotation matrix around the y-axis for angle {np.degrees(theta)} degrees:\n", rot_y[i])
        print(f"Rotation matrix around the z-axis for angle {np.degrees(theta)} degrees:\n", rot_z[i])
        print("----")
