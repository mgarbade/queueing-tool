#!/usr/bin/python3

import re

class Block(object):
    def __init__(self):
        self.values = dict()
        self.values['name'] = 'unknown-job'  # Corrected typo from 'unkown-job' to 'unknown-job'
        self.values['threads'] = 1
        self.values['memory'] = 1024
        self.values['gpus'] = 0
        self.values['hours'] = 1
        self.values['subtasks'] = 1
        self.values['script'] = []

    def check(self):
        try:
            for key in ['name', 'threads', 'memory', 'gpus', 'hours', 'subtasks']:
                original_value = self.values[key]
                if isinstance(self.values[key], int):
                    self.values[key] = max(1, self.values[key])
                elif key == 'gpus':
                    self.values[key] = max(0, self.values[key])
                else:
                    self.values[key] = str(self.values[key])
                print(f"Checked {key}: converted from {original_value} to {self.values[key]}")
        except Exception as e:
            print(f'Parser: Invalid block definition. Key {key} with value {self.values[key]} caused error: {str(e)}. Abort.')
            exit()

    def exists(self, key):
        return key in self.values

    def set_value(self, key, value):
        self.values[key] = value
        print(f"Set {key} to {value}")

    def get_value(self, key):
        assert self.exists(key), f"Key {key} does not exist"
        return self.values[key]

class Block_Parser(object):
    def __init__(self):
        self.blocks = []

    def _parse_block(self, block):
        block[0] = re.sub('gpu=true', 'gpus=1', block[0])
        block[0] = re.sub('gpu=false', 'gpus=0', block[0])
        meta = re.sub('\\).*', '', re.sub('.*\\(', '', block[0])).split(',')
        parsed_block = Block()
        for param in meta:
            key, value = param.split('=')
            key = key.strip()
            value = value.strip()
            if parsed_block.exists(key):
                parsed_block.set_value(key, value)
        parsed_block.set_value('script', block[1:])
        parsed_block.check()
        return parsed_block

    def parse(self, script):
        try:
            f = open(script, 'r')
            content = f.read().split('\\n')
            f.close()
        except Exception as e:
            print(f'Parser: script {script} could not be opened. Error: {str(e)}')
            exit()

        block_starts = []
        for i, line in enumerate(content):
            if line.startswith('#block'):
                block_starts.append(i)
        block_starts.append(len(content))
        blocks = []
        for i in range(len(block_starts) - 1):
            blocks.append(content[block_starts[i]:block_starts[i + 1]])
        if not blocks:
            print(f'Error: No block defined in {script}')
            exit()
        parsed_blocks = []
        for block in blocks:
            parsed_blocks.append(self._parse_block(block))
        return parsed_blocks

# Uncomment to test parsing
# p = Block_Parser()
# p.parse('script.sh')
