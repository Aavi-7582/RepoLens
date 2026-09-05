from tree_sitter import Language, Parser
import tree_sitter_python as ts_python


PYTHON_LANGUAGE = Language(ts_python.language())

python_parser = Parser(PYTHON_LANGUAGE)


def parse_python_code(source_code: str):
    tree = python_parser.parse(
        source_code.encode("utf-8")
    )

    return tree


def extract_python_chunks(source_code: str):
    tree = parse_python_code(source_code)

    chunks = []

    def walk(node):
        if node.type in {
            "function_definition",
            "class_definition"
        }:

            start = node.start_byte
            end = node.end_byte

            content = source_code.encode(
                "utf-8"
            )[start:end].decode("utf-8")

            name_node = node.child_by_field_name("name")

            symbol_name = None

            if name_node:
                symbol_name = source_code[
                    name_node.start_byte:name_node.end_byte
                ]

            chunks.append({
                "chunk_type": node.type,
                "symbol_name": symbol_name,
                "content": content
            })

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    return chunks