from gobstuf.stuf.brp.base_request import StufRequest


class IngeschrevenpersonenStufRequest(StufRequest):
    template = 'ingeschrevenpersonen.xml'
    content_root_elm = 'soapenv:Body BG:npsLv01'
    soap_action = 'http://www.egem.nl/StUF/sector/bg/0310/npsLv01Integraal'

    BSN_LENGTH = 9

    replace_paths = {
        'bsn': 'BG:gelijk BG:inp.bsn'
    }

    def validate(self, args):
        # print("VALIDATE BSN")
        bsn = args['bsn']
        if len(bsn) != self.BSN_LENGTH:
            name = "burgerservicenummer"
            if len(bsn) < self.BSN_LENGTH:
                invalid_param = {
                    "code": "minLength",
                    "reason": f"Waarde is korter dan minimale lengte {self.BSN_LENGTH}."
                }
            else:
                invalid_param = {
                    "code": "maxLength",
                    "reason": f"Waarde is langer dan maximale lengte {self.BSN_LENGTH}."
                }
            invalid_param['name'] = name
            return self.params_errors([name], [invalid_param])

        return super().validate(args)
