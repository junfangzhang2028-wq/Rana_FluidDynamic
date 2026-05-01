from flask import Flask, jsonify, request, abort
from marshmallow import fields
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from aqbackend.outputs import *

app = Flask(__name__)
ma = Marshmallow(app)
CORS(app, resources={r"/solve": {"origins": ["http://aqueousoutflow.ads.northwestern.edu",
                                             "https://aqueousoutflow.ads.northwestern.edu",
                                             "http://localhost:8000",
                                             "http://0.0.0.0:8000"]}})
# CORS(app, resources={r"/solve": {"origins": "http://localhost:8000"}})

def deg2node(deg, num_nodes):
    if deg > 359.7:
        deg = 359.7

    try:
        return int((deg % 360) * num_nodes / 360)
    except Exception:
        raise ValueError('Invalid location specified.')


def process_args(args):
    if type(args) != dict:
        raise TypeError("Internal server error")

    if args['mode'] != 'constant flow':
        if 'qt' in args:
            args.pop('qt')
        if 'iop' not in args:
            raise ValueError('IOP must be defined unless constant flow mode is specified.')

        if args['iop'] is None:
            raise ValueError('IOP must be defined unless constant flow mode is specified.')

    else:
        if 'iop' in args:
            args.pop('iop')
        if 'qt' not in args:
            raise ValueError('Flowrate must be defined if constant flow mode is specified.')

        if args['qt'] is None:
            raise ValueError('Flowrate must be defined if constant flow mode is specified.')

    mode = args.pop('mode')
    constants = args.pop('constants')

    n = 30
    m = 40
    if constants['n'] is not None:
        n = int(constants['n'])

    if constants['m'] is not None:
        m = int(constants['m'])

    num_nodes = n * m

    args2rem = []
    for arg in args:
        if args[arg] is None:
            args2rem += [arg]

        elif arg == "rtm":
            args2rem += [arg]
            if args["variable_rtm"]:
                rtm = np.zeros(n*m)
                for hour in args["rtm"]:
                    rtm[(hour["hour"] - 1)*100:hour["hour"]*100] = hour["resistance"] * 100

                constants["rtm"] = rtm

        elif arg == "h0":
            args2rem += [arg]
            if args["variable_h0"]:
                h0 = np.zeros(n*m)
                for seg in args["h0"]:
                    h0[(seg["seg"] - 1)*m: seg["seg"]*m] = seg["height"]

                constants["h0"] = h0

        elif arg in constants:
            args2rem += [arg]

        elif arg == 'trabeculotomies':
            trabeculotomies = []
            # args['trabeculotomies'] = json.loads(args['trabeculotomies'].replace("'", '"'))

            if type(args['trabeculotomies']) == dict:
                args['trabeculotomies'] = [args['trabeculotomies']]

            for trab in args['trabeculotomies']:
                try:
                    trabeculotomies += [(deg2node(float(trab['start']), num_nodes), deg2node(trab['end'], num_nodes))]

                except Exception:
                    raise ValueError('Both Start and End must be specified for a trabeculotomy')

            args['trabeculotomies'] = trabeculotomies

        elif arg == 'sinusotomies':
            sinusotomies = []
            # args['sinusotomies'] = json.loads(args['sinusotomies'].replace("'", '"'))

            if type(args['sinusotomies']) == dict:
                args['sinusotomies'] = [args['sinusotomies']]

            for sinus in args['sinusotomies']:
                try:
                    sinusotomies += [(deg2node(float(sinus['start']), num_nodes), deg2node(sinus['end'], num_nodes))]

                except Exception:
                    raise ValueError('Both Start and End must be specified for a sinusotomy')

            args['sinusotomies'] = sinusotomies

        elif arg == 'yag_holes':
            yag_holes = []
            # args['yag_holes'] = json.loads(args['yag_holes'].replace("'", '"'))

            if type(args['yag_holes']) == dict:
                args['yag_holes'] = [args['yag_holes']]

            for hole in args['yag_holes']:
                yag_holes += [deg2node(float(hole['loc']), num_nodes)]

            args['yag_holes'] = yag_holes

        elif arg == 'stents':
            stents = []
            # args['stents'] = json.loads(args['stents'].replace("'", '"'))

            if type(args['stents']) == dict:
                args['stents'] = [args['stents']]

            for stent in args['stents']:
                try:
                    s = md.Stent(**stent['stent'])
                    stents += [(deg2node(float(stent['loc']), num_nodes),
                                s)]

                except Exception:
                    raise ValueError('Location must be specified for all stents')

            args['stents'] = stents

        elif arg == 'ccs':
            ccs = []
            # args['ccs'] = json.loads(args['ccs'].replace("'", '"'))

            if type(args['ccs']) == dict:
                args['ccs'] = [args['ccs']]

            for cc in args['ccs']:
                ccs += [(deg2node(float(cc['loc']), num_nodes), float(cc['g_ratio']))]

            args['ccs'] = ccs

    for arg in args2rem:
        args.pop(arg)

    return args, constants, mode


class Conditions:
    def __init__(self, mode, iop, qt, geometry, unconventional, trabeculotomies, sinusotomies, yag_holes, stents, ccs, rtm, constants):
        self.mode = mode
        self.iop = iop
        self.qt = qt
        self.geometry = geometry
        self.unconventional = unconventional
        self.trabeculotomies = trabeculotomies
        self.sinusotomies = sinusotomies
        self.yag_holes = yag_holes
        self.stents = stents
        self.ccs = ccs
        self.rtm = rtm
        self.constants = constants


class ConditionsSchema(ma.Schema):
    mode = fields.Str(allow_none=True)
    iop = fields.Float(allow_none=True)
    qt = fields.Float(allow_none=True)
    geometry = fields.Str(allow_none=True)
    unconventional = fields.Boolean(allow_none=True)
    variable_rtm = fields.Boolean(allow_none=True)
    variable_h0 = fields.Boolean(allow_none=True)
    trabeculotomies = fields.List(fields.Dict(keys=fields.Str(), values=fields.Float(allow_none=True)))
    sinusotomies = fields.List(fields.Dict(keys=fields.Str(), values=fields.Float(allow_none=True)))
    yag_holes = fields.List(fields.Dict(keys=fields.Str(), values=fields.Float(allow_none=True)))
    stents = fields.List(fields.Dict(keys=fields.Str(), values=fields.Field(allow_none=True)))
    ccs = fields.List(fields.Dict(keys=fields.Str(), values=fields.Float()))
    rtm = fields.List(fields.Dict(keys=fields.Str(), values=fields.Float()), allow_none=True)
    h0 = fields.List(fields.Dict(keys=fields.Str(), values=fields.Float()), allow_none=True)
    constants = fields.Dict(keys=fields.Str(), values=fields.Float())


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# @app.before_request
# def block_method():
#     ip = request.environ.get('REMOTE_ADDR')
#     if ip in ip_ban_list:
#         abort(403)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/solve', methods=['POST'])
def get_solution():

    conditions = ConditionsSchema().load(request.get_json())
    # print(conditions)

    try:
        args, constants, mode = process_args(conditions.data)

        if mode == 'constant pressure':
            return jsonify(solve_cp(**args, **constants))

        elif mode == 'constant flow':
            return jsonify(solve_cf(**args, **constants))

    except Exception as err:
        raise InvalidUsage(err.with_traceback(), status_code=400)


if __name__ == '__main__':
    app.run(debug=True)
