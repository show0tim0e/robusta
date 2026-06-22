from math import ceil

from torch import Tensor


def adapt_input_channels(
    weight: Tensor,
    input_channels: int,
) -> Tensor:

    _, source_channels, _, _ = weight.shape


    if input_channels == source_channels:
        return weight.clone()


    if input_channels == 1:
        return weight.mean(
            dim=1,
            keepdim=True,
        )


    if input_channels < source_channels:
        return weight[:, :input_channels].clone()


    repeat_factor = ceil(
        input_channels / source_channels
    )

    weight = weight.repeat(
        1,
        repeat_factor,
        1,
        1,
    )


    return weight[:, :input_channels]