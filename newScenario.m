%% scenario defines the name, epoch, and current time of a simulation
classdef newScenario
    properties
        %% Model
        name = 'MatlabSimulation'
        epoch = datestr(now)
        mu = 3.986004418e14;    %m^3/s^2
        dt = 1                  %s
        T = 15                  %s
        
        %% Origin epoch
        a = 6738e3              %m
        ecc = 0                 %deg
        inc = 98.45             %deg
        Om = 0                  %deg
        om = 0                  %deg
        nu = 0                  %deg
    end
    properties (Dependent)
        n                       %1/s
        TP                      %s
    end
    methods
        function obj = scneario(name)
            if nargin > 0
                obj.name = name;
            end
        end
        % Mean anamoly
        function n = get.n(obj)
            n = sqrt(obj.mu/obj.a^3);
        end
        % Orbital period
        function TP = get.TP(obj)
            TP = 2*pi*sqrt(obj.a^3/obj.mu);
        end
        % Create STK scenario
        function [app,root] =  createSTKscenario(scenario)
            % Open STK
            app = actxserver('STK11.application');
            root = app.Personality2;
            
            % Create scenario
            root.ExecuteCommand(sprintf('New / Scenario %s',scenario.name));
            root.ExecuteCommand('SetAnalysisTimePeriod * "1 Jan 2018 00:00:00" "1 Feb 2018 00:00:00"');
            
            % Create origin
            root.ExecuteCommand('New / */Satellite Origin');
            root.ExecuteCommand(sprintf('SetState */Satellite/Origin Classical TwoBody UseScenarioInterval 60 ICRF "1 Jan 2018" %f %f %f 0 90 180',scenario.a,scenario.ecc,scenario.inc));
            root.ExecuteCommand('VO * ObjectStateInWin Show off Object Satellite/Origin WindowId 1');
            root.ExecuteCommand('VO * ViewFromTo Normal From Satellite/Origin To Satellite/Origin');
            root.ExecuteCommand('VO */Satellite/Origin SetVectorGeometry Add RIC Show On');
            root.ExecuteCommand('SetAnimation * AnimationMode xRealTime');
            root.ExecuteCommand('Animate * Reset');
        end
    end
    
end