#!/usr/bin/env cwl-runner

# This is a sample CWL workflow file for testing Mudag

cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1

outputs:
  output:
    type: stdout

stdout: output.txt 