import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def run_change_detection(
    before_image,
    after_image,
    output_paths,
):
    """
    Performs SSIM-based change detection between two images.

    Args:
        before_image (str | Path):
            Path to the before image.

        after_image (str | Path):
            Path to the after image.

        output_paths (dict):
            OutputManager paths.

    Returns:
        dict
    """

    # ==========================================================
    # LOAD IMAGES
    # ==========================================================

    before = cv2.imread(str(before_image))
    after = cv2.imread(str(after_image))

    if before is None:
        raise FileNotFoundError(
            f"Unable to load image: {before_image}"
        )

    if after is None:
        raise FileNotFoundError(
            f"Unable to load image: {after_image}"
        )

    # ==========================================================
    # RESIZE TO MATCH
    # ==========================================================

    height = min(before.shape[0], after.shape[0])
    width = min(before.shape[1], after.shape[1])

    before = cv2.resize(
        before,
        (width, height)
    )

    after = cv2.resize(
        after,
        (width, height)
    )

    # ==========================================================
    # CONVERT TO GRAYSCALE
    # ==========================================================

    before_gray = cv2.cvtColor(
        before,
        cv2.COLOR_BGR2GRAY
    )

    after_gray = cv2.cvtColor(
        after,
        cv2.COLOR_BGR2GRAY
    )

    # ==========================================================
    # SSIM
    # ==========================================================

    score, diff = ssim(
        before_gray,
        after_gray,
        full=True
    )

    diff = (diff * 255).astype("uint8")

    print(f"\nSSIM Similarity Score : {score:.4f}")

    # ==========================================================
    # THRESHOLD
    # ==========================================================

    thresh = cv2.threshold(
        diff,
        0,
        255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )[1]

    # ==========================================================
    # MORPHOLOGICAL CLEANUP
    # ==========================================================

    kernel_open = np.ones((5, 5), np.uint8)
    kernel_close = np.ones((9, 9), np.uint8)

    thresh = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        kernel_open
    )

    thresh = cv2.morphologyEx(
        thresh,
        cv2.MORPH_CLOSE,
        kernel_close
    )

    # ==========================================================
    # REMOVE SMALL REGIONS
    # ==========================================================

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        thresh,
        connectivity=8
    )

    min_area = 500

    filtered = np.zeros_like(thresh)

    for i in range(1, num_labels):

        area = stats[i, cv2.CC_STAT_AREA]

        if area > min_area:
            filtered[labels == i] = 255

    thresh = filtered

    # ==========================================================
    # CHANGE PERCENTAGE
    # ==========================================================

    change_pixels = np.count_nonzero(thresh)

    total_pixels = thresh.size

    change_percentage = (
        change_pixels / total_pixels
    ) * 100

    print(
        f"Change Detected : {change_percentage:.2f}%"
    )

    # ==========================================================
    # DRAW CHANGED REGIONS
    # ==========================================================

    result = after.copy()

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    region_count = 0

    for contour in contours:

        area = cv2.contourArea(contour)

        if area > min_area:

            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(
                result,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )

            cv2.putText(
                result,
                "Change",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )

            region_count += 1

    # ==========================================================
    # SAVE RESULTS
    # ==========================================================

    cv2.imwrite(
        str(output_paths["change_binary"]),
        thresh
    )

    cv2.imwrite(
        str(output_paths["change_map"]),
        result
    )

    print("Change map saved.")
    print("Binary change map saved.")

    # ==========================================================
    # RETURN RESULTS
    # ==========================================================

    return {

        "similarity_score": round(
            score,
            4,
        ),

        "change_percentage": round(
            change_percentage,
            2,
        ),

        "regions_detected": region_count,

        "change_binary_path": str(
            output_paths["change_binary"]
        ),

        "change_map_path": str(
            output_paths["change_map"]
        ),

    }