import mido

GRID_SIZE = 8

def pad_to_note(row, col):
    return 36 + row * GRID_SIZE + col

def note_to_pad(note):
    index = note - 36
    return index // GRID_SIZE, index % GRID_SIZE


class MidiController:
    def __init__(self, port_name):
        outputs = mido.get_output_names()
        inputs = mido.get_input_names()

        if port_name not in outputs or port_name not in inputs:
            raise RuntimeError(
                f"MIDI device '{port_name}' not found.\n"
                f"Available outputs: {outputs}\n"
                f"Available inputs: {inputs}"
            )

        self.outport = mido.open_output(port_name)
        self.inport = mido.open_input(port_name)

    def light_pad(self, row, col, velocity):
        note = pad_to_note(row, col)
        msg = mido.Message('note_on', note=note, velocity=velocity)
        self.outport.send(msg)
