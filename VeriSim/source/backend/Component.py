class Comp(object):
    """
    This is the base class of specific circuit components classes.
    """
    class Name(object):
        """
        This class defines all the name of the components in the circuit.
        """
        SPLITTER = "Splitter"
        PIN = "Pin"
        CONSTANT = "Constant"
        BIT_EXTENDER = "Bit Extender"
        NOT = "NOT Gate"
        AND = "AND Gate"
        OR = "OR Gate"
        NAND = "NAND Gate"
        NOR = "NOR Gate"
        XOR = "XOR Gate"
        XNOR = "XNOR Gate"
        ODDPARITY = "Odd Parity"
        EVENPARITY = "Even Parity"
        MULTIPLEXER = "Multiplexer"
        DEMULTIPLEXER = "Demultiplexer"
        DECODER = "Decoder"
        BITSELECTOR = "BitSelector"
        ADDER = "Adder"
        SUBTRACTOR = "Subtractor"
        MULTIPLIER = "Multiplier"
        DIVIDER = "Divider"
        COMPARATOR = "Comparator"
        SHIFTER = "Shifter"
        REGISTER = "Register"


    class Lib(object):
        """
        This class defines all the library of the components in the circuit
        """
        WIRING = 0
        GATES = 1
        PLEXERS = 2
        ARITHMETIC = 3
        MEMORY = 4
        # IO, BASE remian unused.
        IO = 5
        BASE = 6

    class Facing(object):
        """
        This class defines value of directions of the components, most default
        direction of which should be EAST, and rarely changed lately.
        """
        EAST = "east"
        WEST = "west"
        NORTH = "north"
        SOUTH = "south"

    class GateSize(object):
        """
        This class defines the size of the Gates, the size should be set
        automatically. FrontEnd shall not change the "size" field of a
        component.
        """
        S20 = 20
        S30 = 30
        S50 = 50
        S70 = 70

    class SelectLoc(object):
        """
        This class defines the select location field of Comp.Name.PLEXERS class.
        Two option: Bottom/Left(bl, default), Top/Right(tr).
        """
        BOTTOM_LEFT = "br"
        TOP_RIGHT = "tr"

    def __init__(self, name, lib, loc=None):
        self.__lib = lib
        self.__loc = loc
        self.__name = name

    def to_xml(self):
        pass


# Below are Comp.Lib.WIRING classes, including Splitter, Pin, Constant,
# Bit Extender.
# TODO: port, width of splited wire
class Splitter(Comp):
    """
    Splitter class.
    """

    class Appearance(object):
        """
        This class defines the value set of the Splitter appear field.
        Default appearance should be LEFT_HANDED.
        """
        LEFT_HANDED = "left"
        RIGHT_HANDED = "right"
        CENTERED = "center"
        LEGACY = "legacy"

    def __init__(self, fanout, incoming, appear, facing=Comp.Facing.EAST):
        super(Splitter, self).__init__(Comp.Name.SPLITTER, Comp.Lib.WIRING)
        self.appear = appear
        self.facing = facing


# TODO: port
# ?TODO: three state, pull behavior
class Pin(Comp):
    """
    Pin class.
    """

    def __init__(self, width, output:bool, facing=None):
        super(Pin, self).__init__(Comp.Name.PIN, Comp.Lib.WIRING)
        self.width = width
        self.output = output
        if facing != None:
            self.facing = facing
        elif output == False:
            self.facing = Comp.Facing.WEST
        else:
            self.facing = Comp.Facing.EAST


# TODO: port, consistency between vlaue and width.
class Constant(Comp):
    """
    Constant class.
    """

    def __init__(self, width, value, facing=Comp.Facing.EAST):
        super(Constant, self).__init__(Comp.Name.CONSTANT, Comp.Lib.WIRING)
        self.width = width
        self.value = value


# TODO: port, input port when extension type is set input
class BitExtender(Comp):
    """
    Bit Extender class.
    """

    class Type(object):
        """
        This class defines the value set of the Bit Extender type field.
        Default value is ZERO.
        """
        ZERO = "zero"
        ONE = "one"
        SIGN = "sign"
        INPUT = "input"

    def __init__(self, in_width, out_width, type=Type.ZERO):
        super(BitExtender, self).__init__(Comp.Name.BIT_EXTENDER,
                                          Comp.Lib.WIRING)
        self.in_width = in_width
        self.out_width = out_width


# Below are Comp.Lib.GATES classes, including NOT, AND, OR, NAND, NOR, XOR,
# XNOR, Odd Parity, Even Parity.
# TODO: port
# ?TODO: output vlaue(01, 0Z, Z1), negate
class TwoOperandGateShape(Comp):
    """
    Basic template for two operand gate.
    This class is the base class for And, Or, Nand, Nor, Xor, Xnor,
    OddParity, EvenParity
    """

    # Three options for size of such gate:
    # Narrow(30), Medium(50), Wide(70)
    # The size of such gates is often set to medium(50).
    def __init__(self, name, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(TwoOperandGateShape, self).__init__(name, Comp.Lib.GATES)
        self.width = width
        self.inputs = inputs
        self.size = size
        self.facing = facing


# TODO: port
# ?TODO: output vlaue(01, 0Z, Z1)
class Not(Comp):
    """
    NOT Gate class.
    """

    # There are two option for size of NOT Gate. Default size of NOT Gate 
    # is 30(Wide), while the other is 20(Narrow).
    def __init__(self, width, size=Comp.GateSize.S30,
                 facing=Comp.Facing.EAST):
        super(Not, self).__init__(Comp.Name.NOT, Comp.Lib.GATES)
        self.width = width
        self.size = size
        self.facing = facing


class And(TwoOperandGateShape):
    """
    AND Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(And, self).__init__(Comp.Name.AND, width, inputs, size, facing)


class Or(TwoOperandGateShape):
    """
    OR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Or, self).__init__(Comp.Name.OR, width, inputs, size, facing)


class Nand(TwoOperandGateShape):
    """
    NAND Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Nand, self).__init__(Comp.Name.NAND, width, inputs, size, facing)


class Nor(TwoOperandGateShape):
    """
    NOR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Nor, self).__init__(Comp.Name.NOR, width, inputs, size, facing)


class Xor(TwoOperandGateShape):
    """
    OR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Xor, self).__init__(Comp.Name.XOR, width, inputs, size, facing)


class Xnor(TwoOperandGateShape):
    """
    XNOR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Xnor, self).__init__(Comp.Name.XNOR, width, inputs, size, facing)


class OddParity(TwoOperandGateShape):
    """
    Odd Parity Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(OddParity, self).__init__(Comp.Name.ODDPARITY,
                                  width, inputs, size, facing)


class EvenParity(TwoOperandGateShape):
    """
    Even Parity Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(EvenParity, self).__init__(Comp.Name.EVENPARITY,
                                  width, inputs, size, facing)


# Below are Comp.Lib.PLEXERS classes, including Multiplexer, Demultiplexer,
# Decoder, Bit Selector.
# TODO: port
class Multiplexer(Comp):
    """
    Multiplexer class.
    """

    def __init__(self, width, select, enable=True,
                 selloc=Comp.SelectLoc.BOTTOM_LEFT,
                 facing=Comp.Facing.EAST):
        super(Multiplexer, self).__init__(Comp.Name.MULTIPLEXER,
                                          Comp.Lib.PLEXERS)
        self.width = width
        self.select = select
        self.enable = enable
        self.selloc = selloc
        self.facing = facing


# TODO: port
class Demultiplexer(Comp):
    """
    Demultiplexer class.
    """

    def __init__(self, width, select, enable=True,
                 selloc=Comp.SelectLoc.BOTTOM_LEFT,
                 facing=Comp.Facing.EAST):
        super(Demultiplexer, self).__init__(Comp.Name.DEMULTIPLEXER,
                                            Comp.Lib.PLEXERS)
        self.width = width
        self.select = select
        self.enable = enable
        self.selloc = selloc
        self.facing = facing


# TODO: port
class Decoder(Comp):
    """
    Decoder class.
    """

    def __init__(self, select, enable=True, selloc=Comp.SelectLoc.BOTTOM_LEFT,
                 facing=Comp.Facing.EAST):
        super(Decoder, self).__init__(Comp.Name.DECODER, Comp.Lib.PLEXERS)
        self.select = select
        self.enable = enable
        self.selloc = selloc
        self.facing = facing


# TODO: port, consistency between width, group, and select.
class BitSelector(Comp):
    """
    BitSelector class.
    """

    def __init__(self, width, group, facing=Comp.Facing.EAST):
        super(BitSelector, self).__init__(Comp.Name.BITSELECTOR,
                                          Comp.Lib.PLEXERS)
        self.width = width
        self.group = group


# Below are Comp.Lib.ARITHMETIC classes, including Adder, Subtractor, 
# Multiplier, Divider, Comparator, Shifter
# TODO: port
class ArithmeticShape(Comp):
    """
    ArithmeticShape class defines the shape of Comp.Lib.ARITHMETIC classes.
    This class is the base class of Adder, Subtractor, Multiplier, Divider, 
    Comparator, Shifter.
    """

    def __init__(self, width, name):
        super(ArithmeticShape, self).__init__(name, Comp.Lib.ARITHMETIC)
        self.width = width

class Adder(ArithmeticShape):
    """
    Adder class.
    """

    def __init__(self, width):
        super(Adder, self).__init__(width, Comp.Name.ADDER)
        

class Subtractor(ArithmeticShape):
    """
    Subtractor class.
    """

    def __init__(self, width):
        super(Subtractor, self).__init__(width, Comp.Name.SUBTRACTOR)


class Multiplier(ArithmeticShape):
    """
    Multiplier class.
    """

    def __init__(self, width):
        super(Multiplier, self).__init__(width, Comp.Name.MULTIPLIER)


class Divider(ArithmeticShape):
    """
    Divider class.
    """

    def __init__(self, width):
        super(Divider, self).__init__(width, Comp.Name.DIVIDER)


class Comparator(ArithmeticShape):
    """
    Comparator class.
    """
    
    class Mode(object):
        """
        Two option for Comparator mode:
        Unsigned("unsigned"), 2's Complement(None)
        """
        UNSIGNED = "unsigned"
        SIGNED = None

    def __init__(self, width, mode):
        super(Comparator, self).__init__(width, Comp.Name.COMPARATOR)
        self.mode = mode


class Shifter(ArithmeticShape):
    """
    Shifter class.
    """

    class Shift(object):
        """
        This class contains five mode for Shifter.
        """
        LOGICAL_LEFT = "ll"
        LOGICAL_RIGHT = "lr"
        ARITHMETIC_RIGHT = "ar"
        ROTATE_LEFT = "rl"
        ROTATE_RIGHT = "rr"

    def __init__(self, width, shift):
        super(Shifter, self).__init__(width, Comp.Name.SHIFTER)
        self.shift = shift


# Below are Comp.Lib.MEMORY classes, including Register.
class Register(Comp):
    """
    Register class.
    """

    class Trigger(object):
        """
        This class defines four type of register trigger method.
        The default value is FALLING_EDGE.
        """
        FALLING_EDGE = "falling"
        RISING_EDGE = "rising"
        HIGH_LEVEL = "high"
        LOW_LEVEL = "low"

    def __init__(self, width, trigger):
        super(Register, self).__init__(Comp.Name.REGISTER, Comp.Lib.MEMORY)
        self.width = width
        self.trigger = trigger
