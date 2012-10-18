<div id="generic-form" class="box">
	<h2><?= __("Add Comment"); ?></h2>
	<form action="<?= $_SERVER['REQUEST_URI'] ?>" method="post">
		<fieldset>
<?php
if (isset($_REQUEST['comment']) && check_token()) {
	echo '<p>' . __('Comment has been added.') . '</p>';
}
?>
			<div>
				<input type="hidden" name="ID" value="<?= intval($row['ID']) ?>" />
				<input type="hidden" name="token" value="<?= htmlspecialchars($_COOKIE['AURSID']) ?>" />
			</div>
			<p>
				<textarea id="id_comment" name="comment" cols="80" rows="10"></textarea>
			</p>
			<p>
				<input type="submit" value="<?= __("Add Comment") ?>" />
			</p>
		</fieldset>
	</form>
</div>

