# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the data classes for the liquidity provision ABCI application."""
from abc import ABC
from enum import Enum
from types import MappingProxyType
from typing import AbstractSet, Dict, Mapping, Optional, Tuple, Type, cast

from aea.exceptions import enforce

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    BasePeriodState,
)
from packages.valory.skills.liquidity_provision.payloads import (
    StrategyEvaluationPayload,
    StrategyType,
)
from packages.valory.skills.price_estimation_abci.payloads import TransactionType
from packages.valory.skills.price_estimation_abci.rounds import (
    CollectDifferentUntilAllRound,
    CollectSameUntilThresholdRound,
    ConsensusReachedRound,
    DeploySafeRound,
    RandomnessRound,
    RegistrationRound,
    ValidateSafeRound,
)


class Event(Enum):
    """Event enumeration for the liquidity provision demo."""

    DONE = "done"
    EXIT = "exit"
    ROUND_TIMEOUT = "round_timeout"
    NO_MAJORITY = "no_majority"
    WAIT = "wait"
    NO_ALLOWANCE = "no_allowance"


class PeriodState(BasePeriodState):  # pylint: disable=too-many-instance-attributes
    """
    Class to represent a period state.

    This state is replicated by the tendermint application.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        participants: Optional[AbstractSet[str]] = None,
        participant_to_strategy: Optional[
            Mapping[str, StrategyEvaluationPayload]
        ] = None,
        most_voted_strategy: Optional[dict] = None,
    ) -> None:
        """Initialize a period state."""
        super().__init__(participants=participants)
        self._participant_to_strategy = participant_to_strategy
        self._most_voted_strategy = most_voted_strategy

    @property
    def most_voted_strategy(self) -> dict:
        """Get the most_voted_strategy."""
        enforce(
            self._most_voted_strategy is not None,
            "'most_voted_strategy' field is None",
        )
        return cast(dict, self._most_voted_strategy)

    def reset(self) -> "PeriodState":
        """Return the initial period state."""
        return PeriodState(self.participants)


class LiquidityProvisionAbstractRound(AbstractRound[Event, TransactionType], ABC):
    """Abstract round for the liquidity provision skill."""

    @property
    def period_state(self) -> PeriodState:
        """Return the period state."""
        return cast(PeriodState, self._state)

    def _return_no_majority_event(self) -> Tuple[PeriodState, Event]:
        """
        Trigger the NO_MAJORITY event.

        :return: a new period state and a NO_MAJORITY event
        """
        return self.period_state.reset(), Event.NO_MAJORITY


class SelectKeeperMainRound(
    CollectDifferentUntilAllRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper main round."""

    round_id = "select_keeper_main"


class SelectKeeperDeployRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper deploy round."""

    round_id = "select_keeper_deploy"


class SelectKeeperSwapRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper swap round."""

    round_id = "select_keeper_swap"


class SelectKeeperAddAllowanceRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper add allowance round."""

    round_id = "select_keeper_approve"


class SelectKeeperAddLiquidityRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper add liquidity round."""

    round_id = "select_keeper_add_liquidity"


class SelectKeeperRemoveLiquidityRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper remove liquidity round."""

    round_id = "select_keeper_remove_liquidity"


class SelectKeeperRemoveAllowanceRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper remove allowance round."""

    round_id = "select_keeper_remove_allowance"


class SelectKeeperSwapBackRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the select keeper swap back round."""

    round_id = "select_keeper_swap_back"


class StrategyEvaluationRound(
    CollectSameUntilThresholdRound, LiquidityProvisionAbstractRound
):
    """This class represents the strategy evaluation round.

    Input: a set of participants (addresses)
    Output: a set of participants (addresses) and the strategy

    It schedules the WaitRound or the SwapRound.
    """

    round_id = "strategy_evaluation"
    allowed_tx_type = StrategyEvaluationPayload.transaction_type
    payload_attribute = "strategy"

    def end_block(self) -> Optional[Tuple[BasePeriodState, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            state = self.period_state.update(
                participant_to_strategy=MappingProxyType(self.collection),
                most_voted_strategy=self.most_voted_payload,
            )
            event = (
                Event.DONE
                if self.period_state.most_voted_strategy["action"] == StrategyType.GO
                else Event.WAIT
            )
            return state, event
        if not self.is_majority_possible(
            self.collection, self.period_state.nb_participants
        ):
            return self._return_no_majority_event()
        return None


class WaitRound(LiquidityProvisionAbstractRound):
    """This class represents the wait round."""


class SwapRound(LiquidityProvisionAbstractRound):
    """This class represents the swap round."""


class ValidateSwapRound(LiquidityProvisionAbstractRound):
    """This class represents the validate swap round."""


class AllowanceCheckRound(LiquidityProvisionAbstractRound):
    """This class represents the allowance check round."""


class AddAllowanceRound(LiquidityProvisionAbstractRound):
    """This class represents the add allowance back round."""


class ValidateAddAllowanceRound(LiquidityProvisionAbstractRound):
    """This class represents the validate add allowance round."""


class AddLiquidityRound(LiquidityProvisionAbstractRound):
    """This class represents the add liquidity round."""


class ValidateAddLiquidityRound(LiquidityProvisionAbstractRound):
    """This class represents the validate add liquidity round."""


class RemoveLiquidityRound(LiquidityProvisionAbstractRound):
    """This class represents the remove liquidity round."""


class ValidateRemoveLiquidityRound(LiquidityProvisionAbstractRound):
    """This class represents the validate remove liquidity round."""


class RemoveAllowanceRound(LiquidityProvisionAbstractRound):
    """This class represents the remove allowance round."""


class ValidateRemoveAllowanceRound(LiquidityProvisionAbstractRound):
    """This class represents the validate remove allowance round."""


class SwapBackRound(LiquidityProvisionAbstractRound):
    """This class represents the swap back round."""


class ValidateSwapBackRound(LiquidityProvisionAbstractRound):
    """This class represents the svalidate swap back round."""


class LiquidityProvisionAbciApp(AbciApp[Event]):
    """Liquidity Provision ABCI application."""

    initial_round_cls: Type[AbstractRound] = RegistrationRound
    transition_function: AbciAppTransitionFunction = {
        RegistrationRound: {Event.DONE: RandomnessRound},
        RandomnessRound: {
            Event.DONE: SelectKeeperMainRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        SelectKeeperMainRound: {
            Event.DONE: DeploySafeRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        DeploySafeRound: {
            Event.DONE: ValidateSafeRound,
            Event.EXIT: SelectKeeperDeployRound,
        },
        SelectKeeperDeployRound: {
            Event.DONE: DeploySafeRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        ValidateSafeRound: {
            Event.DONE: StrategyEvaluationRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        StrategyEvaluationRound: {
            Event.DONE: SwapRound,
            Event.WAIT: WaitRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        WaitRound: {
            Event.DONE: StrategyEvaluationRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        SwapRound: {
            Event.DONE: ValidateSwapRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
            Event.EXIT: SelectKeeperSwapRound,
        },
        SelectKeeperSwapRound: {
            Event.DONE: SwapRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        ValidateSwapRound: {
            Event.DONE: AllowanceCheckRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        AllowanceCheckRound: {
            Event.DONE: AddLiquidityRound,
            Event.NO_ALLOWANCE: AddAllowanceRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        AddAllowanceRound: {
            Event.DONE: ValidateAddAllowanceRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
            Event.EXIT: SelectKeeperAddAllowanceRound,
        },
        SelectKeeperAddAllowanceRound: {
            Event.DONE: AddAllowanceRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        ValidateAddAllowanceRound: {
            Event.DONE: AddLiquidityRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        AddLiquidityRound: {
            Event.DONE: ValidateAddLiquidityRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
            Event.EXIT: SelectKeeperAddLiquidityRound,
        },
        SelectKeeperAddLiquidityRound: {
            Event.DONE: AddLiquidityRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        ValidateAddLiquidityRound: {
            Event.DONE: RemoveLiquidityRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        RemoveLiquidityRound: {
            Event.DONE: ValidateRemoveLiquidityRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
            Event.EXIT: SelectKeeperRemoveLiquidityRound,
        },
        SelectKeeperRemoveLiquidityRound: {
            Event.DONE: RemoveLiquidityRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        ValidateRemoveLiquidityRound: {
            Event.DONE: RemoveAllowanceRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        RemoveAllowanceRound: {
            Event.DONE: ValidateRemoveAllowanceRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
            Event.EXIT: SelectKeeperRemoveAllowanceRound,
        },
        SelectKeeperRemoveAllowanceRound: {
            Event.DONE: SwapRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        ValidateRemoveAllowanceRound: {
            Event.DONE: SwapBackRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        SwapBackRound: {
            Event.DONE: ValidateSwapBackRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
            Event.EXIT: SelectKeeperSwapBackRound,
        },
        SelectKeeperSwapBackRound: {
            Event.DONE: SwapBackRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
        ValidateSwapBackRound: {
            Event.DONE: ConsensusReachedRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
            Event.NO_MAJORITY: RegistrationRound,
        },
    }
    event_to_timeout: Dict[Event, float] = {
        Event.EXIT: 5.0,
        Event.ROUND_TIMEOUT: 30.0,
    }
