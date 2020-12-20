from math import ceil
from math import log2
from abc import abstractmethod


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

    # Unique identifier of a component.
    __ID = 0

    def __init__(self, name, lib, loc=None):
        self.__id = Comp.__ID
        Comp.__ID += 1
        self.__lib = lib
        self.__name = name
        self.loc = loc
        # dict: {Port.TAG: Port}
        self.ports = {}

    def get_desc(self):
        return "{} {}".format(self.__name, self.__id)

    def get_downstream_comps(self):
        """
        return set of downstream components
        """
        down = set()
        for self_port in self.ports.values():
            for down_port in self_port.down:
                down.add(down_port.owner)
        return down

    @abstractmethod
    def set_loc(self, loc: tuple):
        """
        Set location to component and ports.
        """
        pass

    def to_xml(self):
        pass


class Port(object):
    """
    Each instance of this class represents a port on the components of the
    circuit.
    "width" of the port should be in [1, 2, ..., 32].
    "dir" indicates direction of the port, True means input, False means output.
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

    class Dir(object):
        """
        Direction of the port, including input and output direction.
        """
        INPUT = "input port"
        OUTPUT = "output port"

    def __init__(self, owner: Comp, width: int, dir: Dir, loc=None, name=None):
        assert (width >= 0 and width <= 32), \
               "Port width {} out of range.".format(width)
        self.owner = owner
        self.width = width
        self.dir = dir
        self.loc = loc
        self.name = name
        self.upper = None   # upperstream of the data stream
        self.down = []      # list of downstream of the data stream

    @classmethod
    def link(cls, src_comp: Comp, src_port: str,
             dst_comp: Comp, dst_port: str):
        """
        Note that port in the link should be in the right order since data
        stream between the ports has direction.
        """
        src = src_comp.ports[src_port]
        dst = dst_comp.ports[dst_port]
        # Linked ports should have the same width.
        assert (src.width == dst.width), \
            "Linked ports {}:{}, {}:{} have different width." \
            .format(src_comp.get_desc(), src_port,
                    dst_comp.get_desc(), dst_port)
        # Source port could have multiple downstream port, while destination
        # port have just one upperstream port.
        src.down.append(dst)
        assert (dst.upper == None), "Multiple upperstream port for {}:{}." \
            .format(dst_comp.get_desc(), dst_port)
        dst.upper = src

    def set_loc(self, loc: tuple):
        self.loc = loc

    def get_loc(self):
        pass


# Below are Comp.Lib.WIRING classes, including Splitter, Pin, Constant,
# Bit Extender.
class Splitter(Comp):
    """
    Splitter class.
    Ports: combined, out0 ~ out(N-1)(N = len(fanout))
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

    def __init__(self, fanout_tuple: tuple, incoming: int, combine: bool):
        """
        Parameter 
        combine: determines whether the Splitter is used as a combiner 
            or a splitter.
        fanout_tuple: tuple consist of width of each fanout in appropriate
            order. Numbers in the front of the tuple represent lower bits of
            the splitted value.
        "incoming" and "fanout_tuple" should comply with this rule:
            incoming >= sum(fanout_tuple)
        """
        # incoming >= sum(fanout_tuple)
        assert (incoming >= sum(fanout_tuple)), \
               "incoming and fanout_tuple inconsistency occured at Splitter" \
               "construction, (incoming, fanout_tuple) = ({}, {})." \
               .format(incoming, fanout_tuple)
        # Construct Splitter component.
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
        # If the component is used as combiner, set "combine" port direction
        # to OUTPUT, otherwise set it to INPUT.
        if combine == True:
            combine_dir, out_dir = Port.Dir.OUTPUT, Port.Dir.INPUT
        else:
            combine_dir, out_dir = Port.Dir.INPUT, Port.Dir.OUTPUT
        self.ports.setdefault("combined", Port(self, incoming, combine_dir))
        for i in range(self.fanout):
            self.ports.setdefault(Port.Tag.OUT + str(i),
                                  Port(self, fanout_tuple[i], out_dir))


# TODO?: three state, pull behavior
class Pin(Comp):
    """
    Pin class.
    Ports: inout.
    """

    def __init__(self, width, output: bool, facing=None):
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
        if output == True:
            inout_dir = Port.Dir.OUTPUT
        else:
            inout_dir = Port.Dir.INPUT
        self.ports.setdefault("inout", Port(self, width, inout_dir))

    def set_loc(self, loc: tuple):
        self.loc = loc
        self.ports["inout"].set_loc(loc)


class Constant(Comp):
    """
    Constant class.
    Ports: out.
    """

    def __init__(self, width, value, facing=Comp.Facing.EAST):
        """
        Parameter
        value: value in the Constant component is treated as binary code
            instead of a signed or unsigned integer.
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
        self.ports.setdefault(Port.Tag.OUT, Port(self, width, Port.Dir.OUTPUT))


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
        self.ports.setdefault(Port.Tag.IN, 
                              Port(self, in_width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT, 
                              Port(self, out_width, Port.Dir.OUTPUT))
        if type == BitExtender.Type.INPUT:
            self.ports.setdefault("prefix", Port(self, 1, Port.Dir.INPUT))


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
        self.ports.setdefault(Port.Tag.IN, Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT, Port(self, width, Port.Dir.OUTPUT))


# TODO?: output vlaue(01, 0Z, Z1), negate
class GeneralGate(Comp):
    """
    Basic template for gates. It supports three or more inputs.
    This class is the base class for And, Or, Nand, Nor, Xor, Xnor,
    OddParity, EvenParity
    Ports: in0 ~ in(N-1)(N = inputs), out
    """

    # Three options for size of such gate:
    # Narrow(30), Medium(50), Wide(70)
    # The size of such gates is often set to medium(50).
    def __init__(self, name, width, inputs: int, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(GeneralGate, self).__init__(name, Comp.Lib.GATES)
        self.width = width
        self.inputs = inputs
        self.size = size
        self.facing = facing
        # Create ports for two-operand gates
        for i in range(inputs):
            self.ports.setdefault(Port.Tag.IN + str(i),
                                  Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT, 
                              Port(self, width, Port.Dir.OUTPUT))

    def set_loc(self, loc: tuple):
        self.loc = loc
        assert (self.size == Comp.GateSize.S50), \
               "Gatesize should be S50, hasn't support other size yet, " \
               "Current size is {}.".format(self.size)
        # Set location for ports.
        self.ports[Port.Tag.OUT].set_loc(loc)
        x = loc[0] - 50
        if self.inputs < 5:
            self.ports[Port.Tag.IN + "0"].set_loc((x, loc[1] - 20))
            self.ports[Port.Tag.IN + str(self.inputs - 1)] \
                .set_loc((x, loc[1] + 20))
            if self.inputs == 3:
                self.ports[Port.Tag.IN + "1"].set_loc((x, loc[1]))
            if self.inputs == 4:
                self.ports[Port.Tag.IN + "1"].set_loc((x, loc[1] - 10))
                self.ports[Port.Tag.IN + "2"].set_loc((x, loc[1] + 10))
        else:
            offset = self.inputs // 2
            for i in range(offset + 1):
                self.ports[Port.Tag.IN + str(i)] \
                    .set_loc((x, loc[1] - 10 * (offset - i)))
                self.ports[Port.Tag.IN + str(self.inputs - 1 - i)] \
                    .set_loc((x, loc[1] + 10 * (offset - i)))


class And(GeneralGate):
    """
    AND Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(And, self).__init__(Comp.Name.AND, width, inputs, size, facing)


class Or(GeneralGate):
    """
    OR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Or, self).__init__(Comp.Name.OR, width, inputs, size, facing)


class Nand(GeneralGate):
    """
    NAND Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Nand, self).__init__(Comp.Name.NAND, width, inputs, size, facing)


class Nor(GeneralGate):
    """
    NOR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Nor, self).__init__(Comp.Name.NOR, width, inputs, size, facing)


class Xor(GeneralGate):
    """
    OR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Xor, self).__init__(Comp.Name.XOR, width, inputs, size, facing)


class Xnor(GeneralGate):
    """
    XNOR Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(Xnor, self).__init__(Comp.Name.XNOR, width, inputs, size, facing)


class OddParity(GeneralGate):
    """
    Odd Parity Gate class.
    """

    def __init__(self, width, inputs, size=Comp.GateSize.S50,
                 facing=Comp.Facing.EAST):
        super(OddParity, self).__init__(Comp.Name.ODDPARITY,
                                  width, inputs, size, facing)


class EvenParity(GeneralGate):
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
    Ports: in0 ~ in(N-1)(N = 2^select), out, sel, en
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
            self.ports.setdefault(Port.Tag.IN + str(i),
                                  Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT, Port(self, width, Port.Dir.OUTPUT))
        self.ports.setdefault(Port.Tag.SEL, Port(self, select, Port.Dir.INPUT))
        if enable == True:
            self.ports.setdefault(Port.Tag.EN, Port(self, 1, Port.Dir.INPUT))


class Demultiplexer(Comp):
    """
    Demultiplexer class.
    Ports: in, out0 ~ out(N-1)(N = 2^select), sel, en
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
        self.ports.setdefault(Port.Tag.IN, Port(self, width, Port.Dir.INPUT))
        for i in range(pow(2, select)):
            self.ports.setdefault(Port.Tag.OUT + str(i),
                                  Port(self, width, Port.Dir.OUTPUT))
        self.ports.setdefault(Port.Tag.SEL, Port(self, select, Port.Dir.INPUT))
        if enable == True:
            self.ports.setdefault(Port.Tag.EN, Port(self, 1, Port.Dir.INPUT))


class Decoder(Comp):
    """
    Decoder class.
    Ports: sel, out0 ~ out(N-1)(N = 2^select), en
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
        self.ports.setdefault(Port.Tag.SEL, Port(self, select, Port.Dir.INPUT))
        for i in range(pow(2, select)):
            self.ports.setdefault(Port.Tag.OUT + str(i),
                                  Port(self, 1, Port.Dir.OUTPUT))
        if enable == True:
            self.ports.setdefault(Port.Tag.EN, Port(self, 1, Port.Dir.INPUT))


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
        self.ports.setdefault(Port.Tag.IN, Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT, Port(self, group, Port.Dir.OUTPUT))
        self.ports.setdefault(Port.Tag.SEL, Port(self, select, Port.Dir.INPUT))


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
            self.ports.setdefault(Port.Tag.IN + "1",
                                  Port(self, width, Port.Dir.INPUT))
            self.ports.setdefault(Port.Tag.IN + "2",
                                  Port(self, width, Port.Dir.INPUT))
            self.ports.setdefault(Port.Tag.OUT,
                                  Port(self, width, Port.Dir.OUTPUT))

class Adder(ArithmeticShape):
    """
    Adder class.
    Ports: in1, in2, out, cin(carry in, 1 bit), cout(carry out, 1 bit)
    """

    def __init__(self, width):
        super(Adder, self).__init__(width, Comp.Name.ADDER, auto_port=True)
        # Create ports for Adder components part of which is created in the
        # ArithmeticShape initializer.
        self.ports.setdefault(Port.Tag.CIN, Port(self, 1, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.COUT, Port(self, 1, Port.Dir.OUTPUT))
        

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
        self.ports.setdefault(Port.Tag.CIN, Port(self, 1, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.COUT, Port(self, 1, Port.Dir.OUTPUT))


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
        self.ports.setdefault(Port.Tag.CIN, Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.COUT, Port(self, width, Port.Dir.OUTPUT))


class Divider(ArithmeticShape):
    """
    Divider class.
    Ports: in1, in2, out, cin(dividend upper), cout(remainder)
    """

    def __init__(self, width):
        super(Divider, self).__init__(width, Comp.Name.DIVIDER, auto_port=True)
        # Create ports for Divider components part of which is created in 
        # the ArithmeticShape initializer.
        self.ports.setdefault(Port.Tag.CIN, Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.COUT, Port(self, width, Port.Dir.OUTPUT))


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
        self.ports.setdefault(Port.Tag.IN + "A",
                              Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.IN + "A",
                              Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT + "g",
                              Port(self, 1, Port.Dir.OUTPUT))
        self.ports.setdefault(Port.Tag.OUT + "e",
                              Port(self, 1, Port.Dir.OUTPUT))
        self.ports.setdefault(Port.Tag.OUT + "l",
                              Port(self, 1, Port.Dir.OUTPUT))


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
        self.ports.setdefault(Port.Tag.IN + "1",
                              Port(self, width, Port.Dir.INPUT))
        shift_dis_width = ceil(log2(width))
        self.ports.setdefault(Port.Tag.IN + "2",
                              Port(self, shift_dis_width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT, Port(self, width, Port.Dir.OUTPUT))


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
        self.ports.setdefault(Port.Tag.IN, Port(self, width, Port.Dir.INPUT))
        self.ports.setdefault(Port.Tag.OUT, Port(self, width, Port.Dir.OUTPUT))
        self.ports.setdefault(Port.Tag.EN, Port(self, 1, Port.Dir.INPUT))
        self.ports.setdefault("clk", Port(self, 1, Port.Dir.INPUT))
        self.ports.setdefault("clr", Port(self, 1, Port.Dir.INPUT))
