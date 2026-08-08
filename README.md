# ASIC Reverse-Engineering Puzzle

This repository provides the files for the Jane Street ASIC reverse-engineering puzzle! See the [blog post](https://blog.janestreet.com/can-you-reverse-engineer-an-asic/) for more details. Once you figure it out, submit your answer [here](https://docs.google.com/forms/d/e/1FAIpQLScNCnfZ1wC4HbARwynUZ25EKZyqJIzXM_5H5aHom-QeAhE6FA/viewform) along with a brief description of how you did it. Submissions close on **September 4th, 2026.**

![Event Countdown](<img src="http://s.mmgo.io/t/DH08"/>)

### Puzzle GDS

The puzzle GDS is in this repository, in the file named `puzzle.gds`. You can preview it using [KLayout](https://www.klayout.de/) or the [TinyTapeout Online GDS Viewer](https://gds-viewer.tinytapeout.com/).

See `example_inputs.vcd` which shows some inputs being fed to the design (unfortunately, not the correct inputs to make `success` go high!). You can view it using [Surfer](https://surfer-project.org/) or a similar tool.

To help you get started, below is an image with some hints. The region labelled as "output generator" is safe to ignore during your initial reverse-engineering steps, but you'll need to simulate it to get your final answer!

![](layout.png)

### Warm-up Puzzle

To familiarize yourself with the flow and help develop your tools, we've put together a small example design and run it through a very similar flow to the one used for the real thing! The example design consists of two shift registers, an adder, and a comparator, outputting success if `A + B == 496`.

You'll find the following files related to the warm-up puzzle:

- `warmup/00_source.v`: The original Verilog source code of the example design
- `warmup/01_netlist.v`: Synthesized netlist comprising of a list of standard cells
  and connections
- `warmup/02_netlist_with_power_rails.v`: Netlist with VDD and GND rails added
- `warmup/03_post_place_and_route.def`: Physical layout of cells and routing
  connections, corresponding to cell and net names.
- `warmup/04_final.gds`: The final manufacturable layout file, with many internal names
  removed

### Hints
- The circuit is physically arranged to hint at its functionality, so look closely at the layout!
- There is one section of the design that is used to generate the output but does not affect the [success] output. You can safely ignore it for the initial reverse-engineering steps.
- You’ll need to come up with a way to simulate the underlying circuit to test your solution and get the final output!
- You’ll know you have the correct solution when the [success] output signal goes high. Don’t forget to toggle [rst_n] before each input attempt.
- We hid a few fun Easter eggs in the circuit and in the repository (including in parts you don’t need to look at to solve the main puzzle), see if you can spot them once you’re done with the puzzle.
