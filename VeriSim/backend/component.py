from math import ceil
from math import log2


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
        # dict: {Port.TAG: Port}
        self.ports = {}

    def to_xml(self):
        pass


class Port(object):
    """
    Each instance of this class represents a port on the components of the
    circuit.
    The value of width of the port should be included in [1, 2, ..., 32]
    """

    class Tag(object):
        """
        Tag of ports identify the port in a component.
        This is just part of the defined type, while some type are not defined
        here. Undefined type can be found in the corresponding components
        classes.
        """
        IN = "in"           # general input port
        OUT = "out"         # general output port
        EN = "en"           # enable port
        SEL = "sel"         # select port for PLEXERS
        CIN = "cin"         # carry in port
        COUT = "cout"       # carry out port

    def __init__(self, width: int, loc=None, name=None):
        assert (width >= 0 and width <= 32), \
               "Port width {} out of range.".format(width)
        self.width = width
        self.loc = loc
        self.name = name
        self.linkedPorts = []

    @classmethod
    def link(cls, src_comp: Comp, src_port: str,
             dst_comp: Comp, dst_port: str):
        """
        Note that port in the link should be in the right order since data
        stream between the ports has direction.
        """
        pass


# Below are Comp.Lib.WIRING classes, including Splitter, Pin, Constant,
# Bit Extender.
class Splitter(Comp):
    """
    Splitter class.
    Ports: combined, out0 ~ outN(N = len(fanout))
    """

    class Appearance(object):
        """
        This class defines the value set of the Splitter appear field.
        Used as splitter or combiner should have different appearance.
        Default appearance of a splitter should be LEFT_HANDED, while the 
        appearance of a combiner should default to RIGHT_HANDED.
        """
        LEFT_HANDED = "left"
        RIGHT_HANDED = "right"
        CENTERED = "center"
        LEGACY = "legacy"

    def __init__(self, fanout_tuple: tuple, incoming, combine: bool):
        """
        Parameter 
        combine: determines whether the Splitter is used as a combiner 
            or a splitter.
        fanout_tuple: tuple consist of width of each fanout in appropriate order.
            Numbers in the front of the tuple represent lower bits of the splitted
            value.
        """
        super(Splitter, self).__init__(Comp.Name.SPLITTER, Comp.Lib.WIRING)
        self.fanout = len(fanout_tuple)
        self.incoming = incoming
        if combine == False:
            self.appear = Splitter.Appearance.LEFT_HANDED
            self.facing = Comp.Facing.EAST
        else:
            self.appear = Splitter.Appearance.RIGHT_HANDED
            self.facing = Comp.Facing.WEST
        # Create ports for Splitter components.
        self.ports.setdefault("combined", Port(incoming))
        for i in range(self.fanout):
            self.ports.setdefault(Port.Tag.OUT + str(i), Port(fanout_tuple[i]))


# TODO?: three state, pull behavior
class Pin(Comp):
    """
    Pin class.
    Ports: inout.
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
        # Create ports for Pin components.
        self.ports.setdefault("inout", Port(width))


class Constant(Comp):
    """
    Constant class.
    Ports: out.
    """

    def __init__(self, width, value, facing=Comp.Facing.EAST):
        """
        Parameter
        value: value in the Constant component is treated as binary code instead
            of a signed or unsigned integer.
        "width" and "value" should comply with this rule:
            - 2 ^ (width - 1) <= value <= 2 ^ width - 1.
        While the rule is the bottom line of the logosim software, complying
        with it can not guarantee correctness of the source code.
        """
        # Check consistency of with and value
        floor = - pow(2, width - 1)
        ceiling = pow(2, width) - 1
        assert (value >= floor and value <= ceiling), \
                "Parameter inconsisitency at Constant constructor, " \
                "(width, value) = ({}, {}).".format(width, value)
        # Construct Constant component.
        super(Constant, self).__init__(Comp.Name.CONSTANT, Comp.Lib.WIRING)
        self.width = width
        self.value = value
        # Create ports for Constant components.
        self.ports.setdefault(Port.Tag.OUT, Port(width))

    def __check_consistency(self):
        """
        Check if a binary data with such width have the ability to represent
        the value, so this should be called after the width and value is set.
        """
        floor = - pow(2, self.width - 1)
        ceiling = pow(2, self.width) - 1
        if self.value < floor or self.value > ceiling:
            raise ValueError()


class BitExtender(Comp):
    """
    Bit Extender class.
    Ports: in, out, prefix(on when type is set to INPUT)
    """

    class Type(object):
        """
        This class defines the value set of the Bit Extender type field.
        Default value is ZERO. 
        INPUT type allows user to determine the prefix dynamically.
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
        # Create ports for BitExtender components.
        self.ports.setdefault(Port.Tag.IN, Port(in_width))
        self.ports.setdefault(Port.Tag.OUT, Port(out_width))
        if type == BitExtender.Type.INPUT:
            self.ports.setdefault("prefix", Port(1))


# Below are Comp.Lib.GATES classes, including NOT, AND, OR, NAND, NOR, XOR,
# XNOR, Odd Parity, Even Parity.
# TODO?: output vlaue(01, 0Z, Z1)
class Not(Comp):
    """
    NOT Gate class.
    Ports: in, out
    """

    # There are two option for size of NOT Gate. Default size of NOT Gate 
    # is 30(Wide), while the other is 20(Narrow).
    def __init__(self, width, size=Comp.GateSize.S30,
                 facing=Comp.Facing.EAST):
        super(Not, self).__init__(Comp.Name.NOT, Comp.Lib.GATES)
        self.width = width
        self.size = size
        self.facing = facing
        self.ports.setdefault(Port.Tag.IN, Port(width))
        self.ports.setdefault(Port.Tag.OUT, Port(width))


# TODO?: output vlaue(01, 0Z, Z1), negate
class TwoOperandGateShape(Comp):
    """
    Basic template for gates. It supports three or more inputs though it is
    named TwoOperandGateShape.
    This class is the base class for And, Or, Nand, Nor, Xor, Xnor,
    OddParity, EvenParity
    Ports: in0 ~ inN(N = inputs), out
    """

    # Three options for size of such gate:
    # Narrow(30), Medium(50), Wide(70)
    # The size of such gates is often set to medium(50).
    def __init__(self, name, width, inputs: int, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(TwoOperandGateShape, self).__init__(name, Comp.Lib.GATES)
        self.width = width
        self.inputs = inputs
        self.size = size
        self.facing = facing
        # Create ports for two-operand gates
        for i in range(inputs):
            self.ports.setdefault(Port.Tag.IN + str(i), Port(width))
        self.ports.setdefault(Port.Tag.OUT, Port(width))


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
class Multiplexer(Comp):
    """
    Multiplexer class.
    Ports: in0 ~ inN(N = 2^select), out, sel, en
    """

    def __init__(self, width, select: int, enable=False,
                 selloc=Comp.SelectLoc.BOTTOM_LEFT,
                 facing=Comp.Facing.EAST):
        # 0 <= select <= 5
        assert (0 <= select and select <= 5), \
               "Parameter select {} out of range at Multiplexer constructor." \
               .format(select)
        # Construct Multiplexer component.
        super(Multiplexer, self).__init__(Comp.Name.MULTIPLEXER,
                                          Comp.Lib.PLEXERS)
        self.width = width
        self.select = select
        self.enable = enable
        self.selloc = selloc
        self.facing = facing
        # Create ports for Multiplexer components.
        for i in range(pow(2, select)):
            self.ports.setdefault(Port.Tag.IN + str(i), Port(width))
        self.ports.setdefault(Port.Tag.OUT, Port(width))
        self.ports.setdefault(Port.Tag.SEL, Port(select))
        if enable == True:
            self.ports.setdefault(Port.Tag.EN, Port(1))


class Demultiplexer(Comp):
    """
    Demultiplexer class.
    Ports: in, out0 ~ outN(N = 2^select), sel, en
    """

    def __init__(self, width, select, enable=False,
                 selloc=Comp.SelectLoc.BOTTOM_LEFT,
                 facing=Comp.Facing.EAST):
        # 0 <= select <= 5
        assert (0 <= select and select <= 5), \
               "Parameter select {} out of range at Demultiplexer" \
               "constructor.".format(select)
        # Construct Deultiplexer component.
        super(Demultiplexer, self).__init__(Comp.Name.DEMULTIPLEXER,
                                            Comp.Lib.PLEXERS)
        self.width = width
        self.select = select
        self.enable = enable
        self.selloc = selloc
        self.facing = facing
        # Create ports for Demultiplexer components.
        self.ports.setdefault(Port.Tag.IN, Port(width))
        for i in range(pow(2, select)):
            self.ports.setdefault(Port.Tag.OUT + str(i), Port(width))
        self.ports.setdefault(Port.Tag.SEL, Port(select))
        if enable == True:
            self.ports.setdefault(Port.Tag.EN, Port(1))


class Decoder(Comp):
    """
    Decoder class.
    Ports: sel, out0 ~ outN(N = 2^select), en
    """

    def __init__(self, select, enable=False, selloc=Comp.SelectLoc.BOTTOM_LEFT,
                 facing=Comp.Facing.EAST):
        # 0 <= select <= 5
        assert (0 <= select and select <= 5), \
               "Parameter select {} out of range at Decoder constructor." \
               .format(select)
        # Construct Decoder component.
        super(Decoder, self).__init__(Comp.Name.DECODER, Comp.Lib.PLEXERS)
        self.select = select
        self.enable = enable
        self.selloc = selloc
        self.facing = facing
        # Create ports for Decoder components.
        self.ports.setdefault(Port.Tag.SEL, Port(select))
        for i in range(pow(2, select)):
            self.ports.setdefault(Port.Tag.OUT + str(i), Port(1))
        if enable == True:
            self.ports.setdefault(Port.Tag.EN, Port(1))


class BitSelector(Comp):
    """
    BitSelector class.
    Port: in, out, sel
    """

    def __init__(self, width, group, facing=Comp.Facing.EAST):
        # 0 <= select <= 5
        select = ceil(log2(ceil(width / group)))
        assert (0 <= select and select <= 5), \
               "Parameter select {} out of range at Multiplexer constructor." \
               .format(select)
        # Construct Multiplexer component.
        super(BitSelector, self).__init__(Comp.Name.BITSELECTOR,
                                          Comp.Lib.PLEXERS)
        self.width = width
        self.group = group
        # Create ports for BitSelector components.
        self.ports.setdefault(Port.Tag.IN, Port(width))
        self.ports.setdefault(Port.Tag.OUT, Port(group))
        self.ports.setdefault(Port.Tag.SEL, Port(select))


# Below are Comp.Lib.ARITHMETIC classes, including Adder, Subtractor, 
# Multiplier, Divider, Comparator, Shifter
class ArithmeticShape(Comp):
    """
    ArithmeticShape class defines the shape of Comp.Lib.ARITHMETIC classes.
    This class is the base class of Adder, Subtractor, Multiplier, Divider, 
    Comparator, Shifter.
    Ports: in1, in2, out. This ports are created only for +, -, *, /, thus 
    Comparator and Shifter should never set "auto_port" to Ture. 
    """

    def __init__(self, width, name, auto_port=False):
        super(ArithmeticShape, self).__init__(name, Comp.Lib.ARITHMETIC)
        self.width = width
        # Create general ports for +, -, *, /.
        if auto_port == True:
            self.ports.setdefault(Port.Tag.IN + "1", Port(width))
            self.ports.setdefault(Port.Tag.IN + "2", Port(width))
            self.ports.setdefault(Port.Tag.OUT, Port(width))

class Adder(ArithmeticShape):
    """
    Adder class.
    Ports: in1, in2, out, cin(carry in, 1 bit), cout(carry out, 1 bit)
    """

    def __init__(self, width):
        super(Adder, self).__init__(width, Comp.Name.ADDER, auto_port=True)
        # Create ports for Adder components part of which is created in the
        # ArithmeticShape initializer.
        self.ports.setdefault(Port.Tag.CIN, Port(1))
        self.ports.setdefault(Port.Tag.COUT, Port(1))
        

class Subtractor(ArithmeticShape):
    """
    Subtractor class.
    Ports: in1, in2, out, cin(borrow in, 1 bit), cout(borrow out, 1 bit)
    """

    def __init__(self, width):
        super(Subtractor, self).__init__(width, Comp.Name.SUBTRACTOR,
                                         auto_port=True)
        # Create ports for Subtractor components part of which is created in 
        # the ArithmeticShape initializer.
        self.ports.setdefault(Port.Tag.CIN, Port(1))
        self.ports.setdefault(Port.Tag.COUT, Port(1))


class Multiplier(ArithmeticShape):
    """
    Multiplier class.
    Ports: in1, in2, out, cin(carry in), cout(carry out)
    """

    def __init__(self, width):
        super(Multiplier, self).__init__(width, Comp.Name.MULTIPLIER,
                                         auto_port=True)
        # Create ports for Multiplier components part of which is created in 
        # the ArithmeticShape initializer.
        self.ports.setdefault(Port.Tag.CIN, Port(width))
        self.ports.setdefault(Port.Tag.COUT, Port(width))


class Divider(ArithmeticShape):
    """
    Divider class.
    Ports: in1, in2, out, cin(dividend upper), cout(remainder)
    """

    def __init__(self, width):
        super(Divider, self).__init__(width, Comp.Name.DIVIDER, auto_port=True)
        # Create ports for Divider components part of which is created in 
        # the ArithmeticShape initializer.
        self.ports.setdefault(Port.Tag.CIN, Port(width))
        self.ports.setdefault(Port.Tag.COUT, Port(width))


class Comparator(ArithmeticShape):
    """
    Comparator class.
    Ports: inA, inB, outg(greater), oute(equal), outl(less)
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
        # Create ports for Comparator components.
        self.ports.setdefault(Port.Tag.IN + "A", Port(width))
        self.ports.setdefault(Port.Tag.IN + "A", Port(width))
        self.ports.setdefault(Port.Tag.OUT + "g", Port(1))
        self.ports.setdefault(Port.Tag.OUT + "e", Port(1))
        self.ports.setdefault(Port.Tag.OUT + "l", Port(1))


class Shifter(ArithmeticShape):
    """
    Shifter class.
    Ports: in1, in2(shift distance), out
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

    def __init__(self, width, shift: Shift):
        super(Shifter, self).__init__(width, Comp.Name.SHIFTER)
        # Set shift mode for the Shifter, not shift distance.
        self.shift = shift
        # Create ports for Shifter components.
        self.ports.setdefault(Port.Tag.IN + "1", Port(width))
        shift_dis_width = ceil(log2(width))
        self.ports.setdefault(Port.Tag.IN + "2", Port(shift_dis_width))
        self.ports.setdefault(Port.Tag.OUT, Port(width))


# Below are Comp.Lib.MEMORY classes, including Register.
class Register(Comp):
    """
    Register class.
    Ports: in(Data in), out(Output), en(enable), clk(clock), clr(clear)
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

    def __init__(self, width, trigger: Trigger):
        super(Register, self).__init__(Comp.Name.REGISTER, Comp.Lib.MEMORY)
        self.width = width
        self.trigger = trigger
        # Create ports for Register components.
        self.ports.setdefault(Port.Tag.IN, Port(width))
        self.ports.setdefault(Port.Tag.OUT, Port(width))
        self.ports.setdefault(Port.Tag.EN, Port(1))
        self.ports.setdefault("clk", Port(1))
        self.ports.setdefault("clr", Port(1))
